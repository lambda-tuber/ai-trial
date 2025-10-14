from PySide6.QtWidgets import QApplication, QWidget, QLabel, QDialog, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout
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
        self.zip_dat = zip_dat


        self.setWindowTitle("立ち絵画像選択ダイアログ")

        self.parts = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
        self.part_widgets = {}
        for cat in self.parts:
            file_names = list(zip_dat[cat].keys())
            w = pvv_mcp_server.avatar.mod_ymm_part.AvatarPartWidget(cat, file_names)
            self.part_widgets[cat] = w

        self.setup_gui()

        # タイマー
        self.frame_timer_interval = 25
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.update_frame)
        self.frame_timer.start(self.frame_timer_interval)


    def update_frame(self):
        base_image = None
        painter = None
        
        for cat in self.parts:
            png_file = self.part_widgets[cat].update()
            if png_file:
                png_dat = self.zip_dat[cat][png_file]
                
                # バイトデータからQImageを作成
                part_image = QImage()
                part_image.loadFromData(png_dat)
                
                # 最初のパーツでベース画像を作成
                if base_image is None:
                    base_width = part_image.width()
                    base_height = part_image.height()
                    base_image = QImage(base_width, base_height, QImage.Format_ARGB32)
                    base_image.fill(Qt.transparent)
                    painter = QPainter(base_image)
                
                # パーツを中央揃えで描画
                x = (base_image.width() - part_image.width()) // 2
                y = (base_image.height() - part_image.height()) // 2
                painter.drawImage(x, y, part_image)
        
        scale = 0.5
        # ベース画像が作成されていればラベルに設定
        if base_image is not None and painter is not None:
            painter.end()
            pixmap_org = QPixmap.fromImage(base_image)
            new_width = int(pixmap_org.width() * scale)
            new_height = int(pixmap_org.height() * scale)
            pixmap = pixmap_org.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.center_label.setPixmap(pixmap)




    def setup_gui(self):

        # ----------------------------------------------------
        # 3. 3x3 グリッドレイアウトの作成と配置
        # ----------------------------------------------------
        main_layout = QVBoxLayout(self)

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(10) # グリッド間のスペースを設定
        
        # 3x3 グリッドの配置順序を定義 (中央のインデックス: 4)
        # 0 1 2
        # 3 4 5
        # 6 7 8 (8つのウィジェットと中央のラベルで合計9セルを使用)
        widget_keys = ['目', '眉', '顔',
                       '口',       '髪',
                       '体', '後', '他']
        
        for i in range(9):
            row = i // 3  # 行インデックス (0, 1, 2)
            col = i % 3   # 列インデックス (0, 1, 2)
            
            if i == 4:
                # 3x3 グリッドの中央 (インデックス 4) にラベルを配置
                self.center_label = QLabel()
                self.center_label.setAlignment(Qt.AlignCenter)
                # サイズは画像に合わせて自動調整
                self.center_label.setScaledContents(False)
                self.center_label.setStyleSheet("border: 1px solid gray;")
                
                # グリッドセル内で水平・垂直ともに中央揃え
                grid_layout.addWidget(self.center_label, row, col, Qt.AlignCenter)

            else:
                # 8つのウィジェットを中央セルを避けて配置
                # widget_keys は parts の ['後', '体', '顔', '髪', '口', '目', '眉', '他']
                
                # 中央セル (i=4) をスキップするため、ウィジェットリストのインデックスを調整
                widget_index = i
                if i > 4:
                    widget_index = i - 1
                    
                cat_key = widget_keys[widget_index]
                widget_to_add = self.part_widgets[cat_key]
                
                grid_layout.addWidget(widget_to_add, row, col)

        # 4. メインレイアウトにグリッドウィジェットを追加
        main_layout.addWidget(grid_widget)
        
        self.setLayout(main_layout)



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
    png_dat = defaultdict(dict)
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
                    png_dat[cat][fname] = file_content_bytes



    print(png_dat.keys())
    app = QApplication(sys.argv)
    dialog = AvatarLayerDialog(png_dat)
    dialog.show()
    sys.exit(app.exec())