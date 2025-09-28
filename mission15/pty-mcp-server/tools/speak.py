import requests
import io
import sounddevice as sd
import soundfile as sf
import asyncio
import re
import sys

BASE_URL = "http://127.0.0.1:50021"  # Voicevox Engine デフォルトポート
#SPEAKER_ID = 37 # 四国めたん ひそひそ 綾波
#SPEAKER_ID = 6 # 四国めたん ツンツン リツコ
SPEAKER_ID = 7 # ずんだもん ツンツン  アスカ
#SPEAKER_ID = 38 # ずんだもん ひそひそ ロキシー
#SPEAKER_ID = 10 # 雨晴はう ノーマル みくるさん
#SPEAKER_ID = 107 # 東北ずんこ　みくるさん
#SPEAKER_ID = 61 # 中国うさぎ　ロキシー
#SPEAKER_ID = 47 # ナースロボ　ロキシー
#SPEAKER_ID = 94 # 中部つるぎ ノーマル 少佐
SPEAKER_ID = 14 # 冥鳴ひまり　長門 綾波
SPEAKER_ID = 54 # 春歌ナナ　タチコマ
SPEAKER_ID = 43 # 櫻歌ミコ　タチコマ
SPEAKER_ID = 45 # 櫻歌ミコ　タチコマ

#SPEAKER_ID = 11 # 玄野武宏 ノーマル
#SPEAKER_ID = 74 # 琴詠ニア ノーマル
#SPEAKER_ID = 69 # 満別花丸 ノーマル

PITCH_SCALE = 0.0

def list_speakers_and_styles(base_url=BASE_URL):
    """
    Voicevox の話者一覧とスタイル一覧を取得して表示する
    """
    resp = requests.get(f"{base_url}/speakers")
    resp.raise_for_status()
    speakers = resp.json()

    for s in speakers:
        speaker_id = s.get("id")  # 整数ID
        name = s.get("name")
        print(f"Speaker ID: {speaker_id} - 名前: {name}")
        for style in s.get("styles", []):
            style_id = style["id"]
            style_name = style["name"]
            print(f"  Style ID: {style_id} - Style Name: {style_name}")
        print()  # 空行で区切り


def tts_play(text: str, speaker_id: int = SPEAKER_ID):
    # 1. audio_query で音声合成パラメータを取得
    response = requests.post(
        f"{BASE_URL}/audio_query",
        params={"speaker": speaker_id, "text": text}
    )
    response.raise_for_status()
    query = response.json()

    # 2. synthesis で音声データを取得
    response = requests.post(
        f"{BASE_URL}/synthesis",
        params={"speaker": speaker_id},
        headers={"Content-Type": "application/json"},
        json=query
    )
    response.raise_for_status()

    # 3. 音声データを再生
    audio_data, samplerate = sf.read(io.BytesIO(response.content))
    sd.play(audio_data, samplerate)
    sd.wait()


async def tts_play_async(text: str, speaker_id: int = SPEAKER_ID, pitch_scale = PITCH_SCALE, base_url: str = BASE_URL):
    """
    Voicevox OSS Engine を使ってテキストを音声合成し、非同期で再生する関数
    """
    # 1. audio_query で音声合成パラメータを取得
    resp = requests.post(
        f"{base_url}/audio_query",
        params={"speaker": speaker_id, "text": text}
    )
    resp.raise_for_status()
    query = resp.json()
    query["pitchScale"] = pitch_scale

    # 2. synthesis で wav バイナリを取得
    resp = requests.post(
        f"{base_url}/synthesis",
        params={"speaker": speaker_id},
        headers={"Content-Type": "application/json"},
        json=query
    )
    resp.raise_for_status()
    wav_bytes = resp.content

    # 3. メモリ上で再生（非同期対応）
    data, samplerate = sf.read(io.BytesIO(wav_bytes))
    sd.play(data, samplerate)
    await asyncio.to_thread(sd.wait)



def split_sentences(text: str):
    # 句点で区切る（簡易版）
    sentences = re.split(r'(?<=[。！？?!])', text)
    return [s.strip() for s in sentences if s.strip()]


async def speak_async(text: str, speaker_id: int = SPEAKER_ID, pitch_scale = PITCH_SCALE, base_url: str = BASE_URL):
    # for sentence in split_sentences(remove_bracket_text(text)):
    #     await tts_play_async(sentence, speaker_id, pitch_scale, base_url)
    await tts_play_async(remove_bracket_text(text), speaker_id, pitch_scale, base_url)


def remove_bracket_text(text: str) -> str:
    # 丸括弧の中身を削除（全角・半角の両方対応）
    text = re.sub(r'（.*?）', '', text)  # 全角括弧
    text = re.sub(r'\(.*?\)', '', text)  # 半角括弧
    return text.strip()


# 使い方
async def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <speaker_id> <text>")
        sys.exit(1)

    speaker_id = sys.argv[1]
    pitch_scale = sys.argv[2]
    long_text = sys.argv[3]

    await speak_async(long_text, speaker_id, pitch_scale)


if __name__ == "__main__":
    asyncio.run(main())


