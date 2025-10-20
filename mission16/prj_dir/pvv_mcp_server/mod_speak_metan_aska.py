# mod_speak_metan_aska.py

import requests
import sounddevice as sd
import soundfile as sf
import numpy as np
import io
import re
import logging
import time
import pvv_mcp_server.mod_avatar_manager

logger = logging.getLogger(__name__)

def remove_bracket_text(text: str) -> str:
    # 丸括弧の中身を削除（全角・半角の両方対応）
    text = re.sub(r'（.*?）', '', text)  # 全角括弧
    text = re.sub(r'\(.*?\)', '', text)  # 半角括弧
    return text.strip()

def speak_metan_aska(msg: str) -> None:
    """
    四国めたん(style_id=6)を使用してVOICEVOX Web APIで音声合成し、再生する関数
    
    Args:
        msg (str): 発話するメッセージ
    
    Returns:
        None

    Example:
        python -c "from pvv_mcp_server.mod_speak_metan_aska import speak_metan_aska; speak_metan_aska('あんた、バカぁ！？')"

    """
    start = time.perf_counter()
    
    # VOICEVOXのデフォルトURL
    pvv_url = "http://127.0.0.1:50021"
    style_id = 6  # 四国めたん
    pitch_scale=0.02

    # 音声合成用クエリの作成
    query_url = f"{pvv_url}/audio_query"
    query_params = {
        "text": remove_bracket_text(msg),
        "speaker": style_id
    }
    
    # クエリ生成
    query_response = requests.post(query_url, params=query_params)
    query_response.raise_for_status()
    query_data = query_response.json()

    end = time.perf_counter()
    elapsed = end - start
    logger.info(f"mod_speak 1: {elapsed:.3f} 秒")

    start = time.perf_counter()


    # 調整
    query_data["pitchScale"] = pitch_scale

    # 音声合成
    synthesis_url = f"{pvv_url}/synthesis"
    synthesis_params = {
        "speaker": style_id
    }
    synthesis_response = requests.post(
        synthesis_url,
        params=synthesis_params,
        json=query_data
    )
    synthesis_response.raise_for_status()
    end = time.perf_counter()
    elapsed = end - start
    logger.info(f"mod_speak 2: {elapsed:.3f} 秒")
    try:
        start = time.perf_counter()
        pvv_mcp_server.mod_avatar_manager.set_anime_key(style_id, "口パク")
        audio_data, samplerate = sf.read(io.BytesIO(synthesis_response.content), dtype='float32', always_2d=True)
        with sd.OutputStream(samplerate=samplerate, channels=audio_data.shape[1], dtype='float32') as stream:
            stream.write(audio_data)
        end = time.perf_counter()
        elapsed = end - start
        logger.info(f"mod_speak 3: {elapsed:.3f} 秒")
    except Exception as e:
        raise Exception(f"音声再生エラー: {e}")

    finally:
        pvv_mcp_server.mod_avatar_manager.set_anime_key(style_id, "立ち絵")
