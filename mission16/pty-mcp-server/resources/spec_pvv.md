
# 機能仕様
MCP(Model Context Protocl)をハンドルするサーバ機能を提供する。
- MCP起動モード : stdio
- MCP Tools
  - speak
    - 概要 : 引数のパラメータを入力として、voicevox web apiで音声合成し、発話する。
  - speak_metan_aska
    - 概要 : 引数のmsgを、四国めたんが演じるアスカとしてvoicevoxで発話する。
- MCP Resource
  - speakers
    - 概要 : voicevox web apiでspeakers情報を取得する。
  - speaker_info
    - 概要 : voicevox web apiでspeaker情報を取得する。

---

# 詳細設計
## package
- 名前 : pvv_mcp_server
- pkg_dir : <prj_dir>/pvv_mcp_server

## 依存パッケージ
- mcp
- requests
- sounddevice
- numpy

## mainモジュール
- 概要 : エントリポイント。mos_serviceを使用して、MCP Serverを起動する。
- ファイル : <pkg_dir>/main.py 
- 関数 : なし
- 引数
  - version : オプショナル
  - help : オプショナル

## mod_serviceモジュール
- 概要 : MCP Serverクラスを定義する。
- ファイル : <pkg_dir>/mod_service.py 
- MCP Resourdes
  - speakers
    - 概要 : MCPリソース定義。処理は、mod_speakersのspeakers関数に移譲する。
    - 引数 : なし
  - speaker_info
    - 概要 : MCPリソース定義。処理は、mod_speakerのspeaker_info関数に移譲する。
    - 引数
      1. uuid : Voicevox発話者のuuid

- MCP Tools
  - start
    - 概要 : MCPサーバを起動する。
    - 引数 : なし
  - speak
    - 概要 : MCPツール定義。処理は、mod_speakのspeak関数に移譲する。
    - 引数
      1. style_id : voicevox 発話音声を指定するID(必須)
      2. msg : 発話するメッセージ(必須)
      3. speedScale : float 話速。デフォルト 1.0（0.5 で半分の速さ、2.0 で倍速）(オプショナル)
      4. pitchScale : float 声の高さ（ピッチ）。デフォルト 0.0（正規値）。±0.5 程度で自然 (オプショナル)
      5. intonationScale float 抑揚（イントネーション）の強さ。デフォルト 1.0 (オプショナル)
      6. volumeScale float 音量。デフォルト 1.0 (オプショナル)
  - speak_metan_aska
    - 概要 : MCPツール定義。処理は、mod_speak_metan_askaのspeak_metan_aska関数に移譲する。
    - 引数
      1. msg : 発話するメッセージ

## mod_speak_モジュール
- 概要 : voicevox web apiで音声合成し、再生する関数を実装する。
- ファイル : <pkg_dir>/mod_speak.py 
- 関数
  - speak
    - 概要 : voicevox web apiで音声合成し、音声を再生する。
    - 引数 
      1. style_id : voicevox 発話音声を指定するID(必須)
      2. msg : 発話するメッセージ(必須)
      3. speedScale : float 話速。デフォルト 1.0（0.5 で半分の速さ、2.0 で倍速）(オプショナル)
      4. pitchScale : float 声の高さ（ピッチ）。デフォルト 0.0（正規値）。±0.5 程度で自然 (オプショナル)
      5. intonationScale float 抑揚（イントネーション）の強さ。デフォルト 1.0 (オプショナル)
      6. volumeScale float 音量。デフォルト 1.0 (オプショナル)

## mod_speak_metan_askaモジュール
- 概要 : 四国メタンを指定して、voicevox web apiで音声合成し、再生する関数を実装する。
- ファイル : <pkg_dir>/mod_speak_metan_aska.py 
- style_id : 6
- 関数
  - speak_metan_aska
    - 概要 : voicevox web apiで音声合成し、音声を再生する。
    - 引数 
      1. msg : 発話するメッセージ

## mod_speakersモジュール
- 概要 : voicevox web apiでspeakers情報を取得する。
- ファイル : <pkg_dir>/mod_speakers.py 
- 関数
  - speakers
    - 概要 : voicevox web apiでspeakers情報を取得する。
    - 引数 : なし

## mod_speaker_infoモジュール
- 概要 : voicevox web apiでspeaker情報を取得する。
- ファイル : <pkg_dir>/mod_speaker_info.py 
- 関数
  - speaker
    - 概要 : voicevox web apiでspeaker情報を取得する。
    - 引数
      1. speaker_id : 文字列。話者名、または、UUID。
    - 詳細
      1. 引数がUUIDの場合は、Voicevox APIのspeaker_infoにUUIDをリクエストし、話者情報を取得する。
      2. 引数がUUIDではない場合は
          1. mod_speakers.speakers関数で、話者リストを取得する。
          2. 話者名が引数に部分一致する話者を話者リストから検索抽出し、当該話者のUUIDを特定する。
          3. Voicevox APIのspeaker_infoにUUIDをリクエストし、話者情報を取得する。

