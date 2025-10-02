@echo off
REM ================================
REM 実行方法: run_tts.bat "<long_text>"
REM 例: run_tts.bat "世の中に不満があるなら自分を変えろ。それが嫌なら耳と目を閉じ、口を噤んで孤独に暮らせ"
REM クレジット表記
REM 音声合成: VOICEVOX:冥鳴ひまり
REM https://www.meimeihimari.com/terms-of-use?utm_source=chatgpt.com
REM ================================

if "%~1"=="" (
    echo [ERROR] long_text を指定してください（ダブルクオートで囲む必要あり）
    exit /b 1
)

set TEXT=%*
set SPEAKER_ID=14
set PITCH_SCALE=0.0

python "%~dp0speak.py" %SPEAKER_ID% %PITCH_SCALE% "%TEXT%"
