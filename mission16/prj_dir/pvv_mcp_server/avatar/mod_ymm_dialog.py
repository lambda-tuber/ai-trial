from PySide6.QtWidgets import QApplication, QWidget, QLabel, QDialog, QComboBox, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPixmap, QPainter, QImage, QShortcut, QKeySequence
from PySide6.QtCore import Qt, QTimer, QPoint
import sys


class AvatarLayerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("立ち絵レイヤー選択")
        self.resize(900, 600)

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
        for combo in self.left_combos + self.right_combos:
            combo.currentIndexChanged.connect(self.update_preview)

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
        for combo in self.left_combos + self.right_combos:
            key = combo.currentText()
            pix = self.layer_images.get(key)
            if pix:
                painter.drawPixmap(0, 0, pix)

        painter.end()
        self.preview_label.setPixmap(QPixmap.fromImage(base))

