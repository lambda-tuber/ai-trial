from PySide6.QtWidgets import QApplication, QWidget, QLabel, QDialog, QComboBox, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPixmap, QPainter, QImage, QShortcut, QKeySequence
from PySide6.QtCore import Qt, QTimer, QPoint
import sys
import zipfile
import io
from collections import defaultdict

import pvv_mcp_server.avatar.mod_ymm_part

class AvatarLayerDialog(QDialog):
    def __init__(self, zip_dat, parent=None):
        super().__init__(parent)
        self.setWindowTitle("立ち絵画像選択ダイアログ")
        #self.resize(900, 600)

        # 左右のカテゴリ
        self.left_categories = ['後', '体', '顔', '髪']
        self.right_categories = ['口', '目', '眉', '他']

        # 各カテゴリに QComboBox を作成
        self.left_combos = []
        self.right_combos = []

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        for cat in self.left_categories:
            label = QLabel(cat)           # カテゴリ名をラベルとして表示
            left_layout.addWidget(label)

            combo = QComboBox()
            combo.addItem("01.png")       # アイテムは画像名のみ
            combo.addItem("02.png")
            left_layout.addWidget(combo)
            self.left_combos.append(combo)

        for cat in self.right_categories:
            if cat == "目":
                file_names = [t[0] for t in zip_dat[cat]]
                w = pvv_mcp_server.avatar.mod_ymm_part.AvatarPartWidget(cat,file_names)
                self.right_combos.append(w)
            else:
                combo = QComboBox()
                combo.addItem(f"{cat}: 01.png")
                combo.addItem(f"{cat}: 02.png")
                self.right_combos.append(combo)

        # 中央プレビュー
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(400, 500)
        self.preview_label.setStyleSheet("background-color:#222; border:1px solid #666;")

        # レイアウト構築
        layout = QHBoxLayout()

        for combo in self.right_combos:
            right_layout.addWidget(combo)

        layout.addLayout(left_layout)
        layout.addWidget(self.preview_label)
        layout.addLayout(right_layout)
        self.setLayout(layout)

        # 仮の画像パーツを生成（色分け）
        self.layer_images = self.generate_dummy_layers()

        # プルダウン変更でプレビュー更新
        # for combo in self.left_combos + self.right_combos:
        #     combo.currentIndexChanged.connect(self.update_preview)

        # 初期プレビュー表示
        self.update_preview()

    def generate_dummy_layers(self):
        """カテゴリごとのダミー画像を作成"""
        images = {}
        colors = [Qt.red, Qt.green, Qt.blue, Qt.yellow, Qt.cyan, Qt.magenta, Qt.gray, Qt.white]
        cats = self.left_categories + self.right_categories
        for i, cat in enumerate(cats):
            for num in ["01.png", "02.png"]:
                pix = QPixmap(300, 400)
                pix.fill(colors[i % len(colors)])
                painter = QPainter(pix)
                painter.setPen(Qt.black)
                painter.drawText(pix.rect(), Qt.AlignCenter, f"{cat}\n{num}")
                painter.end()
                images[f"{cat}:{num}"] = pix
        return images

    def update_preview(self):
        """現在のプルダウン選択に基づいてプレビュー更新"""
        base = QImage(300, 400, QImage.Format_ARGB32)
        base.fill(Qt.transparent)
        painter = QPainter(base)

        # 左→右の順で合成
        # for combo in self.left_combos + self.right_combos:
        #     key = combo.currentText()
        #     pix = self.layer_images.get(key)
        #     if pix:
        #         painter.drawPixmap(0, 0, pix)

        painter.end()
        self.preview_label.setPixmap(QPixmap.fromImage(base))

if __name__ == "__main__":

    zip_file = "C:\\work\\lambda-tuber\\ai-trial\\mission16\\docs\\ゆっくり霊夢改.zip"

    zip_bytes = None
    with open(zip_file, "rb") as f:
        zip_bytes = f.read()

    # メモリ上で展開
    zip_buffer = io.BytesIO(zip_bytes)
    png_dat = defaultdict(list)
    with zipfile.ZipFile(zip_buffer, 'r', metadata_encoding='cp932') as zf:
        for info in zf.infolist():
            #print(f"ファイル名: {info.filename}")
            with zf.open(info) as file:
                if info.filename.endswith("/"):  # フォルダはスキップ
                    continue
                parts = info.filename.split("/")
                if len(parts) >= 3:
                    file_content_bytes = file.read()
                    cat = parts[-2]  # 「口」「他」などのカテゴリ
                    fname = parts[-1]  # ファイル名
                    print(f"{parts}")
                    png_dat[cat].append((fname, file_content_bytes))



    print(png_dat.keys())
    app = QApplication(sys.argv)
    dialog = AvatarLayerDialog(png_dat)
    dialog.show()
    sys.exit(app.exec())