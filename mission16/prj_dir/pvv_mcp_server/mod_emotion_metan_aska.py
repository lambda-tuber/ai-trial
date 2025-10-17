# mod_speak_metan_aska.py

import requests
import sounddevice as sd
import soundfile as sf
import numpy as np
import io
import re

import pvv_mcp_server.mod_avatar_manager

def emotion_metan_aska(emotion: str) -> None:
    """
    四国めたん(style_id=6)を使用してアバターにワンショットアニメーションする関数
    
    Args:
        emotion: 感情の種類を指定します。
                 以下のいずれかを指定してください。
                 ["えがお", "びっくり", "がーん", "いかり"]
    
    Returns:
        None

    """
    style_id = 6  # 四国めたん

    try:
        pvv_mcp_server.mod_avatar_manager.set_anime_key(style_id, emotion)

    except Exception as e:
        raise Exception(f"音声再生エラー: {e}")

    finally:
        pvv_mcp_server.mod_avatar_manager.set_anime_key(style_id, "立ち絵")
