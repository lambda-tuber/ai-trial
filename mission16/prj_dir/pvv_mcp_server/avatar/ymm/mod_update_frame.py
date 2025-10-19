from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from io import BytesIO
from PIL import Image
import zipfile
import sys
import logging

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# stderrへの出力ハンドラー
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def ymm_update_frame(self):
    """
    フレームを更新(画像合成)
    
    Args:
        self: YmmAvatarWindowのインスタンス
    """
    if not self.zip_data:
        return
    
    # 現在のアニメタイプのダイアログを取得
    dialog = self.ymm_dialogs.get(self.anime_key)
    if not dialog:
        return
    
    try:
        dialog.update_frame()
        pixmap = dialog.get_current_pixmap()

        if not pixmap:
            logger.warning("daialog preview pixmap none.")
            return

        # 表示更新
        self.label.setPixmap(pixmap)
        self.label.adjustSize()
        self.adjustSize()
        
    except Exception as e:
        logger.warning(f"フレーム更新エラー: {e}")
    
    # アニメーションインデックス更新
    # self.anime_index += 1
    # dialog.update_frame_index()
