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
    
    # # current_imageセットを取得
    # current_images = dialog.get_current_images()
    # if not current_images:
    #     return
    
    # try:
    #     # ZIPファイルから画像を読み込んで合成
    #     zip_file = zipfile.ZipFile(BytesIO(self.zip_data))
        
    #     # ベース画像(最初の画像)
    #     base_path = current_images[0]
    #     base_data = zip_file.read(base_path)
    #     base_img = Image.open(BytesIO(base_data)).convert('RGBA')
        
    #     # 残りの画像を重ね合わせ
    #     for img_path in current_images[1:]:
    #         try:
    #             img_data = zip_file.read(img_path)
    #             layer_img = Image.open(BytesIO(img_data)).convert('RGBA')
    #             base_img = Image.alpha_composite(base_img, layer_img)
    #         except Exception as e:
    #             print(f"画像合成エラー: {img_path}, {e}")
        
    #     # 左右反転
    #     if self.flip:
    #         base_img = base_img.transpose(Image.FLIP_LEFT_RIGHT)
        
    #     # 縮尺変更
    #     if self.scale_percent != 100:
    #         new_width = int(base_img.width * self.scale_percent / 100)
    #         new_height = int(base_img.height * self.scale_percent / 100)
    #         base_img = base_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
    #     # PIL ImageをQPixmapに変換
    #     img_byte_arr = BytesIO()
    #     base_img.save(img_byte_arr, format='PNG')
    #     img_byte_arr.seek(0)
        
    #     qimage = QImage.fromData(img_byte_arr.getvalue())
    #     pixmap = QPixmap.fromImage(qimage)
        
    try:
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
