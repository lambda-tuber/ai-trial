# mod_speak_metan_aska.py

import requests
import sounddevice as sd
import numpy as np

def speak_metan_aska(msg: str) -> None:
    """
    四国めたん(style_id=6)を使用してVOICEVOX Web APIで音声合成し、再生する関数
    
    Args:
        msg (str): 発話するメッセージ
    
    Returns:
        None

    Example:
        python -c "from voicevox_mcp_server.mod_speak_metan_aska import speak_metan_aska; speak_metan_aska('あんた、バカぁ！？')"

    """
    # VOICEVOXのデフォルトURL
    voicevox_url = "http://127.0.0.1:50021"
    style_id = 6  # 四国めたん
    
    # 音声合成用クエリの作成
    query_url = f"{voicevox_url}/audio_query"
    query_params = {
        "text": msg,
        "speaker": style_id
    }
    
    # クエリ生成
    query_response = requests.post(query_url, params=query_params)
    query_response.raise_for_status()
    query_data = query_response.json()
    
    # 音声合成
    synthesis_url = f"{voicevox_url}/synthesis"
    synthesis_params = {
        "speaker": style_id
    }
    synthesis_response = requests.post(
        synthesis_url,
        params=synthesis_params,
        json=query_data
    )
    synthesis_response.raise_for_status()
    
    # 音声データの取得（WAVファイル）
    audio_data = synthesis_response.content
    
    # WAVファイルのヘッダーをスキップしてPCMデータを取得
    # 標準的なWAVヘッダーは44バイト
    pcm_data = audio_data[44:]
    
    # int16のバイナリデータをnumpy配列に変換
    audio_array = np.frombuffer(pcm_data, dtype=np.int16)
    
    # float32に正規化（-1.0 to 1.0）
    audio_float = audio_array.astype(np.float32) / 32768.0
    
    # 再生（VOICEVOXのデフォルトサンプリングレートは24000Hz）
    sd.play(audio_float, samplerate=24000)
    sd.wait()


