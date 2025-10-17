import logging
import io
import sys
from collections import defaultdict
import zipfile
import urllib.request
import base64
from pathlib import Path

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


def load_zip_data(source, speaker_id=None):
    """
    画像データを読み込む
    
    Args:
        source: 以下のいずれかの形式
            - ローカルZIPファイルパス (例: "C:\\path\\to\\file.zip")
            - URL (例: "https://example.com/avatar.zip")
            - PNGファイルパス (例: "C:\\path\\to\\image.png")
            - 空文字列 ("") - VOICEVOXのポートレートを使用
        speaker_id: VOICEVOXの話者ID (sourceが空文字列の場合に使用)
    
    Returns:
        dict: パーツカテゴリ別の画像データ辞書
    """
    
    parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
    
    # 1. 空文字列 → VOICEVOXのポートレート
    if not source or source == "":
        return _load_voicevox_portrait(speaker_id)
    
    # 2. URL → ダウンロードしてZIP展開
    if source.startswith("http://") or source.startswith("https://"):
        if source.endswith(".zip"):
            return _load_zip_from_url(source, parts_folder)
    
    # 3. PNGファイル → 「他」カテゴリに設定
    if source.lower().endswith(".png"):
        return _load_single_png(source)
    
    # 4. ローカルZIPファイル → 既存の処理
    if source.lower().endswith(".zip"):
        return _load_local_zip(source, parts_folder)
    
    # 不明な形式
    logger.error(f"不明なsource形式: {source}")
    return _create_empty_zip_data()


def _load_local_zip(zip_path, parts_folder):
    """ローカルZIPファイルを読み込む"""
    try:
        with open(zip_path, "rb") as f:
            zip_bytes = f.read()

        # メモリ上で展開
        zip_buffer = io.BytesIO(zip_bytes)
        zip_data = defaultdict(dict)
        with zipfile.ZipFile(zip_buffer, 'r', metadata_encoding='cp932') as zf:
            for info in zf.infolist():
                with zf.open(info) as file:
                    if not info.filename.endswith(".png"):
                        continue
                    parts = info.filename.split("/")
                    if len(parts) >= 3:
                        file_content_bytes = file.read()
                        cat = parts[-2]  # 「口」「他」などのカテゴリ
                        if cat not in parts_folder:
                            logger.info(f"ZIPファイル: {info.filename}")
                            cat = "他"
                        fname = parts[-1]  # ファイル名
                        zip_data[cat][fname] = file_content_bytes

        logger.info(f"ローカルZIPファイルを読み込みました: {zip_path}")
        return zip_data

    except Exception as e:
        logger.error(f"ローカルZIPファイル読み込みエラー: {e}")
        return _create_empty_zip_data()


def _load_zip_from_url2(url, parts_folder):
    """URLからZIPファイルをダウンロードして読み込む"""
    try:
        logger.info(f"ZIPファイルをダウンロード中: {url}")
        
        # URLからダウンロード
        with urllib.request.urlopen(url) as response:
            zip_bytes = response.read()
        
        logger.info(f"ダウンロード完了: {len(zip_bytes)} bytes")

        # メモリ上で展開
        zip_buffer = io.BytesIO(zip_bytes)
        zip_data = defaultdict(dict)
        with zipfile.ZipFile(zip_buffer, 'r', metadata_encoding='cp932') as zf:
            for info in zf.infolist():
                with zf.open(info) as file:
                    if not info.filename.endswith(".png"):
                        continue
                    parts = info.filename.split("/")
                    if len(parts) >= 3:
                        file_content_bytes = file.read()
                        cat = parts[-2]
                        if cat not in parts_folder:
                            cat = "他"
                        fname = parts[-1]
                        zip_data[cat][fname] = file_content_bytes

        logger.info(f"URLからZIPファイルを読み込みました: {url}")
        return zip_data

    except Exception as e:
        logger.error(f"URL ZIPファイル読み込みエラー: {e}")
        return _create_empty_zip_data()



def _load_zip_from_url(url, parts_folder):
    """URLからZIPファイルをダウンロードして読み込む"""
    try:
        logger.info(f"ZIPファイルをダウンロード中: {url}")

        # 日本語を含むURLを正しくエンコード
        parsed = urllib.parse.urlsplit(url)
        encoded_path = urllib.parse.quote(parsed.path)
        encoded_url = urllib.parse.urlunsplit(
            (parsed.scheme, parsed.netloc, encoded_path, parsed.query, parsed.fragment)
        )

        # URLからダウンロード
        with urllib.request.urlopen(encoded_url) as response:
            zip_bytes = response.read()

        logger.info(f"ダウンロード完了: {len(zip_bytes)} bytes")

        # メモリ上で展開
        zip_buffer = io.BytesIO(zip_bytes)
        zip_data = defaultdict(dict)
        with zipfile.ZipFile(zip_buffer, 'r', metadata_encoding='cp932') as zf:
            for info in zf.infolist():
                with zf.open(info) as file:
                    if not info.filename.endswith(".png"):
                        continue
                    parts = info.filename.split("/")
                    if len(parts) >= 3:
                        file_content_bytes = file.read()
                        cat = parts[-2]
                        if cat not in parts_folder:
                            cat = "他"
                        fname = parts[-1]
                        zip_data[cat][fname] = file_content_bytes

        logger.info(f"URLからZIPファイルを読み込みました: {url}")
        return zip_data

    except Exception as e:
        logger.error(f"URL ZIPファイル読み込みエラー: {e}")
        return defaultdict(dict)


def _load_single_png(png_path):
    """単一PNGファイルを「他」カテゴリに読み込む"""
    try:
        with open(png_path, "rb") as f:
            png_bytes = f.read()
        
        zip_data = _create_empty_zip_data()
        filename = Path(png_path).name
        zip_data["他"][filename] = png_bytes
        
        logger.info(f"PNGファイルを読み込みました: {png_path}")
        return zip_data

    except Exception as e:
        logger.error(f"PNGファイル読み込みエラー: {e}")
        return _create_empty_zip_data()


def _load_voicevox_portrait(speaker_id):
    """VOICEVOXのポートレートを取得"""
    try:
        from pvv_mcp_server.mod_speaker_info import speaker_info
        
        if not speaker_id:
            logger.warning("speaker_idが指定されていません")
            return _create_empty_zip_data()
        
        info = speaker_info(speaker_id)
        portrait_base64 = info.get("portrait")
        
        if not portrait_base64:
            logger.warning(f"speaker_id={speaker_id}のポートレートが見つかりません")
            return _create_empty_zip_data()
        
        # Base64デコード
        png_bytes = base64.b64decode(portrait_base64)
        
        zip_data = _create_empty_zip_data()
        zip_data["他"]["portrait.png"] = png_bytes
        
        logger.info(f"VOICEVOXポートレートを読み込みました: speaker_id={speaker_id}")
        return zip_data

    except Exception as e:
        logger.error(f"VOICEVOXポートレート読み込みエラー: {e}")
        return _create_empty_zip_data()


def _create_empty_zip_data():
    """空のzip_dataを作成"""
    parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
    zip_data = defaultdict(dict)
    
    # 各カテゴリに空の辞書を設定
    for cat in parts_folder:
        zip_data[cat] = {}
    
    return zip_data


if __name__ == "__main__":
    # テスト1: ローカルZIP
    print("=== テスト1: ローカルZIP ===")
    zip_file = "C:\\work\\lambda-tuber\\ai-trial\\mission16\\docs\\ゆっくり霊夢改.zip"
    png_dat = load_zip_data(zip_file)
    print(f"カテゴリ: {list(png_dat.keys())}")
    
    # テスト2: PNG
    print("\n=== テスト2: PNG ===")
    png_file = "C:\\work\\lambda-tuber\\ai-trial\\mission16\\docs\\josei_20_pw\\josei_20_a.png"
    png_dat = load_zip_data(png_file)
    print(f"カテゴリ: {list(png_dat.keys())}")
    
    # テスト3: VOICEVOX
    #print("\n=== テスト3: VOICEVOX ===")
    #png_dat = load_zip_data("", speaker_id="四国めたん")
    #print(f"カテゴリ: {list(png_dat.keys())}")
    
    # テスト4: URL
    print("\n=== テスト4: URL ===")
    url = "http://www.nicotalk.com/sozai/きつねゆっくり/れいむ.zip"
    png_dat = load_zip_data(url)
    print(f"カテゴリ: {list(png_dat.keys())}")