@echo off
REM ================================
REM 実行方法: run_tts.bat "<long_text>"
REM 例: run_tts.bat "世の中に不満があるなら自分を変えろ。それが嫌なら耳と目を閉じ、口を噤んで孤独に暮らせ"
REM クレジット
REM VOICEVOX: No.7
REM https://voiceseven.com/
REM   非商用利用（趣味での動画投稿など）：自由に利用可（ただし禁止事項を守る必要あり）。
REM ================================

if "%~1"=="" (
    echo [ERROR] long_text を指定してください（ダブルクオートで囲む必要あり）
    exit /b 1
)

set TEXT=%*
set SPEAKER_ID=29
set PITCH_SCALE=0.03

python "%~dp0speak.py" %SPEAKER_ID% %PITCH_SCALE% "%TEXT%"
