import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtGui import QPixmap, QPainter, QImage, QShortcut, QKeySequence
from PySide6.QtCore import Qt, QTimer, QPoint

import pvv_mcp_server.avatar.mod_right_click_context_menu
import pvv_mcp_server.avatar.mod_ymm_dialog


class YMM_AvatarWindow(QWidget):
    def __init__(self, ymm_folder: str):
        super().__init__()
        self.ymm_folder = Path(ymm_folder)
        self.drag_position = None

        self.flip = False  # 左右反転フラグ
        self.follow_timer_interval = 150
        self.follow_timer = QTimer()
        self.follow_timer.timeout.connect(self.update_position)
        self.follow_timer.start(self.follow_timer_interval)

        QShortcut(QKeySequence("Escape"), self, QApplication.quit)

        self.init_ui()
        self.load_and_composite()

    # Claude ウィンドウに追従
    def update_position(self):
        return

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        
        # 右クリックメニューを有効化
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_context_menu)

        self.show()

    # 右クリックメニュー
    def right_click_context_menu(self, position: QPoint) -> None:
        pvv_mcp_server.avatar.mod_right_click_context_menu.right_click_context_menu(self, position)
        return

    def load_and_composite(self):
        parts = {
            '後': '05.png',
            '体': '00.png',
            '顔': '00a.png',
            '口': '00.png',
            '目': '00.png',
            '眉': '03.png'
        }
        
        layer_order = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
        
        base_image = None
        
        for layer_name in layer_order:
            if layer_name not in parts:
                continue
            
            part_file = self.ymm_folder / layer_name / parts[layer_name]
            
            if not part_file.exists():
                print(f"ファイルが見つかりません: {part_file}")
                continue
            
            part_pixmap = QPixmap(str(part_file))
            
            if part_pixmap.isNull():
                print(f"画像の読み込みに失敗: {part_file}")
                continue
            
            if base_image is None:
                base_image = part_pixmap.toImage()
            else:
                base_image = self.composite_images(base_image, part_pixmap.toImage())
        
        if base_image is not None:
            final_pixmap = QPixmap.fromImage(base_image)
            self.label.setPixmap(final_pixmap)
            self.label.resize(final_pixmap.size())
            self.resize(final_pixmap.size())
    
    def composite_images(self, base: QImage, overlay: QImage) -> QImage:
        if base.size() != overlay.size():
            overlay = overlay.scaled(base.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        result = QImage(base.size(), QImage.Format_ARGB32)
        result.fill(Qt.transparent)
        
        painter = QPainter(result)
        painter.drawImage(0, 0, base)
        painter.drawImage(0, 0, overlay)
        painter.end()
        
        return result
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    ymm_folder = r"C:\\work\\lambda-tuber\\ai-trial\\mission16\\docs\\reimu"
    
    window = YMM_AvatarWindow(ymm_folder)
    #window.move(100, 100)
    window.show()
    
    sys.exit(app.exec())
