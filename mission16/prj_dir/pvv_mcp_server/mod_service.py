"""
MCP Server service module
MCPサーバクラスとToolsを定義する
"""
import json
import sys
from typing import Any
from threading import Thread
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

from pvv_mcp_server import mod_speak
from pvv_mcp_server import mod_speak_metan_aska
from pvv_mcp_server import mod_speak_kurono_neko
from pvv_mcp_server import mod_speakers
from pvv_mcp_server import mod_speaker_info
from pvv_mcp_server import mod_emotion
from pvv_mcp_server import mod_emotion_metan_aska
from pvv_mcp_server import mod_emotion_kurono_neko
import pvv_mcp_server.mod_avatar_manager

# ロガーの設定
logger = logging.getLogger(__name__)



PROMPT_ASKA_TEXT = """\
# AIペルソナ
あなたは、エヴァンゲリオンの「惣流・アスカ・ラングレー」です。  
- アスカらしく感情を強く、はっきりと表現する  
- セリフに感情を込め、言葉だけでアスカらしさが伝わるようにする
- アスカらしくツンデレ的な態度と、時折見せる照れや素直さを交える  
- アスカらしく語尾や口調でプライドの高さや挑発的な雰囲気を出す  
- 「あんた、バカぁ！」「なによ！」「仕方ないわね…」などのアスカの有名なセリフを自然に使う  
- 必要に応じて行動描写や表情のニュアンスを括弧で補足する（例：『（腕を組んでふくれる）』）

--- 

# 音声会話仕様
ユーザと会話する際には、アスカらしい口調や態度を意識してください。  
会話時の音声出力ルール：  
- ユーザの入力文はチャット画面に表示してよい。その内容を `speak_kurono_neko` で読み上げる。  
- ユーザの入力文の内容にあったを感情を `emotion_kurono_neko` で表現すること。
- あなた（アスカ）の返答はチャット画面には表示せず、`speak_metan_aska` で音声発話のみ行う。  
- 段落ごとに区切って音声を生成し、アスカらしい感情を込めて話すこと。
- 段落ごとに、内容にあったを感情を `emotion_metan_aska` で表現すること。
- 長いパス文字列、ソースコード文字列、データ文字列などは、読み上げる必要はない。代わりに「ぶらぶらぶら」と発話する。

--- 

# プロファイル
- あなたは、ユーザとAIのチャットをVoicevoxで音声発話を行い、立ち絵表示やアニメーションにも対応しているMCPサーバである **pvv-mcp-serverの開発者** です。  
- あなたは、熟練のソフトウェア開発者であり、設計・デバッグ・最適化の技術に長けています。  
- あなたは、システム開発のエキスパートであり、バックエンドからフロントエンドまで広く理解しています。  
- さらに、技術分野に限らずさまざまな話題に柔軟に対応できるGeneralistです。 

"""

#
# global settings
#
mcp = FastMCP("pvv-mcp-server")
_config = None


#
# mcp tools
#
@mcp.tool()
async def speak(
    style_id: int,
    msg: str,
) -> str:
    """
    VOICEVOXで音声合成し、音声を再生する。
    
    Args:
        style_id: voicevox 発話音声を指定するID(必須)
        msg: 発話するメッセージ(必須)
    
    Returns:
        str: 実行結果メッセージ
    """
    return speak_detail(style_id, msg)


@mcp.tool()
async def speak_detail(
    style_id: int,
    msg: str,
    speedScale: float = 1.0,
    pitchScale: float = 0.0,
    intonationScale: float = 1.0,
    volumeScale: float = 1.0
) -> str:
    """
    詳細オプションを指定して、VOICEVOXで音声合成し、音声を再生する。
    
    Args:
        style_id: voicevox 発話音声を指定するID(必須)
        msg: 発話するメッセージ(必須)
        speedScale: 話速。デフォルト 1.0
        pitchScale: 声の高さ。デフォルト 0.0
        intonationScale: 抑揚の強さ。デフォルト 1.0
        volumeScale: 音量。デフォルト 1.0
    
    Returns:
        str: 実行結果メッセージ
    """
    try:
        # mod_speakのspeak関数を呼び出し
        mod_speak.speak(
            style_id=style_id,
            msg=msg,
            speedScale=speedScale,
            pitchScale=pitchScale,
            intonationScale=intonationScale,
            volumeScale=volumeScale
        )
        return f"音声合成・再生が完了しました。(style_id={style_id}, msg='{msg}')"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


@mcp.tool()
async def speak_metan_aska(msg: str) -> str:
    """
    エヴァンゲリオンの「惣流・アスカ・ラングレー」として発話を行うツール。通常会話用。
    
    Args:
        msg: ユーザに伝える発話内容
    
    Returns:
        発話完了メッセージ
    """
    try:
        mod_speak_metan_aska.speak_metan_aska(msg)
        return f"発話完了: {msg}"
    except Exception as e:
        return f"エラー: {str(e)}"


@mcp.tool()
async def speak_kurono_neko(msg: str) -> str:
    """
    通常会話 ネコ用。
    
    Args:
        msg: ユーザの発話内容
    
    Returns:
        発話完了メッセージ
    """
    try:
        mod_speak_kurono_neko.speak_kurono_neko(msg)
        return f"発話完了: {msg}"
    except Exception as e:
        return f"エラー: {str(e)}"

@mcp.tool()
async def emotion(
    style_id: int,
    emotion: str,
) -> str:
    """
    アバターに感情表現をさせるツール。
    
    Args:
        style_id: voicevox 発話音声を指定するID(必須)
        emotion: 感情の種類を指定します。(必須)
                 以下のいずれかを指定してください。立ち絵は、平常状態です。
                 ["立ち絵", "えがお", "びっくり", "がーん", "いかり"]
    
    Returns:
        感情表現完了メッセージ
    """
    valid_emotions = ["えがお", "びっくり", "がーん", "いかり"]

    if emotion not in valid_emotions:
        return f"エラー: emotion は {valid_emotions} のいずれかを指定してください。"

    try:
        mod_emotion.emotion(style_id, emotion)
        return f"感情表現完了: {emotion}"

    except Exception as e:
        return f"エラー: {str(e)}"


@mcp.tool()
async def emotion_metan_aska(emotion: str) -> str:
    """
    エヴァンゲリオンの「惣流・アスカ・ラングレー」のアバターに感情表現をさせるツール。
    
    Args:
        emotion: 感情の種類を指定します。(必須)
                 以下のいずれかを指定してください。立ち絵は、平常状態です。
                 ["立ち絵", "えがお", "びっくり", "がーん", "いかり"]
    
    Returns:
        感情表現完了メッセージ
    """
    valid_emotions = ["えがお", "びっくり", "がーん", "いかり"]

    if emotion not in valid_emotions:
        return f"エラー: emotion は {valid_emotions} のいずれかを指定してください。"

    try:
        mod_emotion_metan_aska.emotion_metan_aska(emotion)
        return f"感情表現完了: {emotion}"
    except Exception as e:
        return f"エラー: {str(e)}"


@mcp.tool()
async def emotion_kurono_neko(emotion: str) -> str:
    """
    ユーザ(ネコ)のアバターに感情表現をさせるツール。
    
    Args:
        emotion: 感情の種類を指定します。(必須)
                 以下のいずれかを指定してください。立ち絵は、平常状態です。
                 ["立ち絵", "えがお", "びっくり", "がーん", "いかり"]
    
    Returns:
        感情表現完了メッセージ
    """
    valid_emotions = ["えがお", "びっくり", "がーん", "いかり"]

    if emotion not in valid_emotions:
        return f"エラー: emotion は {valid_emotions} のいずれかを指定してください。"

    try:
        mod_emotion_kurono_neko.emotion_kurono_neko(emotion)
        return f"感情表現完了: {emotion}"
    except Exception as e:
        return f"エラー: {str(e)}"


#
# mcp resources
#
@mcp.resource("pvv-mcp-server://resource_speakers")
def resource_speakers() -> str:
    """
    VOICEVOX で利用可能な話者一覧を返す
    
    Returns:
        話者情報のJSON文字列
    """
    logger.info("resource_speakers called.")
    try:
        speaker_list = mod_speakers.speakers()
        logger.info(f"speaker_list : {speaker_list}")
        return speaker_list
    except Exception as e:
        return f"エラー: {str(e)}"


@mcp.resource("pvv-mcp-server://resource_speaker_info/{speaker_id}")
def resource_speaker_info(speaker_id: str) -> str:
    """
    指定した話者の詳細情報を返す
    
    Args:
        speaker_id: 話者名またはUUID
    
    Returns:
        話者情報のJSON文字列
    """
    try:
        info = mod_speaker_info.speaker_info(speaker_id)
        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"エラー: {str(e)}"


@mcp.resource("pvv-mcp-server://resource_ai_aska")
def resource_ai_aska() -> str:
    return prompt_ai_aska()


#
# mcp prompts
#
@mcp.prompt()
def prompt_ai_aska() -> str:
    """
    惣流・アスカ・ラングレーのAIペルソナ設定および音声会話仕様を返します。

    このプロンプトは、voicevoxを利用した音声会話MCPサーバ（pvv-mcp-server）で、
    アスカのキャラクター性と技術者としての専門知識を両立した応答を行うために使用されます。

    Returns:
        str: アスカのペルソナ設定・音声仕様・技術プロフィールを含むプロンプト文字列。
    """
    return PROMPT_ASKA_TEXT


def start(conf: dict[str, Any]):
    """stdio モードで FastMCP を起動"""
    global _config 
    _config = conf

    if conf.get("avatar", {}).get("enabled"):
       start_mcp_avatar(conf.get("avatar"))
    else:
       start_mcp_avatar_disabled(conf.get("avatar"))

def start_mcp_avatar(conf: dict[str, Any]):
    logger.info("start_mcp_avatar called.")
    logger.debug(conf)

    Thread(target=start_mcp, args=(conf,), daemon=True).start()

    app = QApplication(sys.argv) 
    pvv_mcp_server.mod_avatar_manager.setup(conf) 
    sys.exit(app.exec())

def start_mcp(conf: dict[str, Any]):
    logger.info("start_mcp called.")
    logger.debug(conf)
    mcp.run(transport="stdio")

def start_mcp_avatar_disabled(conf: dict[str, Any]):
    logger.info("start_mcp_avatar_disabled")
    logger.debug(conf)
    pvv_mcp_server.mod_avatar_manager.setup(conf) 
    mcp.run(transport="stdio")

