
import logging
import io
import sys
from collections import defaultdict
import zipfile

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

def load_zip_data(zip_path):
    """
    ZIPファイルをメモリに読み込む
    
    Args:
        self: YmmAvatarWindowのインスタンス
        zip_path: ZIPファイルのパス
    """
    
    parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']

    try:
        zip_bytes = None
        with open(zip_path, "rb") as f:
            zip_bytes = f.read()

        # メモリ上で展開
        zip_buffer = io.BytesIO(zip_bytes)
        zip_data = defaultdict(dict)
        with zipfile.ZipFile(zip_buffer, 'r', metadata_encoding='cp932') as zf:
            for info in zf.infolist():
                #print(f"ファイル名: {info.filename}")
                with zf.open(info) as file:
                    if not info.filename.endswith(".png"):  # フォルダはスキップ
                        continue
                    parts = info.filename.split("/")
                    if len(parts) >= 3:
                        file_content_bytes = file.read()
                        cat = parts[-2]  # 「口」「他」などのカテゴリ
                        if not cat in parts_folder:
                           logger.info(f"ZIPファイル: {info.filename}")
                           cat = "他"
                        fname = parts[-1]  # ファイル名
                        zip_data[cat][fname] = file_content_bytes

        logger.info(f"ZIPファイルを読み込みました: {zip_path}")
        return zip_data

    except Exception as e:
        logger.warning(f"ZIPファイル読み込みエラー: {e}")


if __name__ == "__main__":

    zip_file = "C:\\work\\lambda-tuber\\ai-trial\\mission16\\docs\\ゆっくり霊夢改.zip"
    zip_file = "C:\\work\\lambda-tuber\\ai-trial\\mission16\\docs\\josei_20_pw.zip"

    png_dat = load_zip_data(zip_file)

    print(png_dat.keys())
