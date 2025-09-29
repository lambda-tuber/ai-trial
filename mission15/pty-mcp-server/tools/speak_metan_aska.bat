@echo off
REM ================================
REM 実行方法: run_tts.bat "<long_text>"
REM 例: run_tts.bat "世の中に不満があるなら自分を変えろ。それが嫌なら耳と目を閉じ、口を噤んで孤独に暮らせ"
REM クレジット
REM VOICEVOX:四国めたん
REM https://zunko.jp/con_ongen_kiyaku.html
REM ================================

if "%~1"=="" (
    echo [ERROR] long_text を指定してください（ダブルクオートで囲む必要あり）
    exit /b 1
)

set TEXT=%*
set SPEAKER_ID=6
set PITCH_SCALE=0.02

python "%~dp0speak.py" %SPEAKER_ID% %PITCH_SCALE% "%TEXT%"
