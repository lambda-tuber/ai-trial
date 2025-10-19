# mod_emotion_zunda_marisa.py

import requests
import sounddevice as sd
import soundfile as sf
import numpy as np
import io
import re

import pvv_mcp_server.mod_avatar_manager
import logging
import sys

# ロガーの設定
logger = logging.getLogger(__name__)


def emotion_zunda_marisa(emotion: str) -> None:
    """
    魔理沙のアバターにワンショットアニメーションする関数
    
    Args:
        emotion: 感情の種類を指定します。
                 以下のいずれかを指定してください。立ち絵は、平常状態です。
                 ["立ち絵", "えがお", "びっくり", "がーん", "いかり"]
    
    Returns:
        感情表現完了メッセージ
    """

    style_id = 3

    try:
        logger.info("emotion_zunda_marisa called")
        pvv_mcp_server.mod_avatar_manager.set_anime_key(style_id, emotion)

    except Exception as e:
        logger.warning(f"emotion error {e}")
        raise Exception(f"emotion error {e}")

    finally:
        logger.info("emotion_zunda_marisa finalize")
        #pvv_mcp_server.mod_avatar_manager.set_anime_key(style_id, "立ち絵")
