# mod_speak_kurono.py

import requests
import sounddevice as sd
import soundfile as sf
import numpy as np
import io
import re

import pvv_mcp_server.mod_avatar_manager

def remove_bracket_text(text: str) -> str:
    # 丸括弧の中身を削除（全角・半角の両方対応）
    text = re.sub(r'（.*?）', '', text)  # 全角括弧
    text = re.sub(r'\(.*?\)', '', text)  # 半角括弧
    return text.strip()

def speak_kurono(msg: str) -> None:
    """
    四国めたん(style_id=6)を使用してVOICEVOX Web APIで音声合成し、再生する関数
    
    Args:
        msg (str): 発話するメッセージ
    
    Returns:
        None

    Example:
        python -c "from pvv_mcp_server.mod_speak_kurono import speak_kurono; speak_kurono('あんた、バカぁ！？')"

    """
    # VOICEVOXのデフォルトURL
    pvv_url = "http://127.0.0.1:50021"
    style_id = 11  # VOICEVOX:玄野武宏 (CV: ガロ)
    
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
    
    try:
        pvv_mcp_server.mod_avatar_manager.set_anime_key(style_id, "口パク")
        audio_data, samplerate = sf.read(io.BytesIO(synthesis_response.content), dtype='float32', always_2d=True)
        with sd.OutputStream(samplerate=samplerate, channels=audio_data.shape[1], dtype='float32') as stream:
            stream.write(audio_data)

    except Exception as e:
        raise Exception(f"音声再生エラー: {e}")

    finally:
        pvv_mcp_server.mod_avatar_manager.set_anime_key(style_id, "立ち絵")
