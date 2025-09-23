import requests
import io
import sounddevice as sd
import soundfile as sf
import asyncio
import re

BASE_URL = "http://127.0.0.1:10101"
SPEAKER_ID = 888753764

def tts_play(text: str, speaker_id: int = SPEAKER_ID, base_url: str = BASE_URL):
    """
    指定したテキストを TTS サーバで合成して、そのまま再生する関数
    """
    # 1. audio_query
    resp = requests.post(
        f"{base_url}/audio_query",
        params={"speaker": speaker_id, "text": text}
    )
    resp.raise_for_status()
    query = resp.json()

    # 2. synthesis
    resp = requests.post(
        f"{base_url}/synthesis",
        params={"speaker": speaker_id},
        headers={"Content-Type": "application/json"},
        json=query
    )
    resp.raise_for_status()
    wav_bytes = resp.content

    # 3. メモリ上で直接再生
    data, samplerate = sf.read(io.BytesIO(wav_bytes))
    sd.play(data, samplerate)
    sd.wait()


async def tts_play_async(text: str, speaker_id: int = SPEAKER_ID, base_url: str = BASE_URL):
    # audio_query
    resp = requests.post(
        f"{base_url}/audio_query",
        params={"speaker": speaker_id, "text": text}
    )
    resp.raise_for_status()
    query = resp.json()

    # synthesis
    resp = requests.post(
        f"{base_url}/synthesis",
        params={"speaker": speaker_id},
        headers={"Content-Type": "application/json"},
        json=query
    )
    resp.raise_for_status()
    wav_bytes = resp.content

    # 再生（非同期対応）
    data, samplerate = sf.read(io.BytesIO(wav_bytes))
    sd.play(data, samplerate)
    await asyncio.to_thread(sd.wait)



def split_sentences(text: str):
    # 句点で区切る（簡易版）
    sentences = re.split(r'(?<=[。！？])', text)
    return [s.strip() for s in sentences if s.strip()]


# 使い方
async def main():
    tts_play("こんにちは、非同期テストです。")

    # long_text = "こんにちは。今日はいい天気ですね！明日は雨が降るかもしれません。"
    # for sentence in split_sentences(long_text):
    #     tts_play(sentence)

    # await tts_play_async("次の文もすぐ再生されます。")

    # long_text = "こんにちは。今日はいい天気ですね！明日は雨が降るかもしれません。"
    # for sentence in split_sentences(long_text):
    #     await tts_play_async(sentence)


if __name__ == "__main__":
    asyncio.run(main())

