@echo off
REM === readfile.bat ===
REM 使い方:
REM   readfile.bat filename.txt
REM   readfile.bat subdir\file.txt
REM   readfile.bat C:\data\subdir\file.txt

setlocal

REM ルートディレクトリを指定
set "ROOT_DIR=C:\work\lambda-tuber\ai-trial\mission16\prj_dir"

if "%~1"=="" (
    echo [ERROR] ファイルパスを指定してください。
    exit /b 1
)

REM ".." を含むパスは禁止
echo %~1 | findstr /C:".." >nul
if %errorlevel%==0 (
    echo [ERROR] 不正なパスです（.. は使用できません）。
    exit /b 1
)

REM 引数が ROOT_DIR で始まるかチェック
echo %~1 | findstr /B /I "%ROOT_DIR%" >nul
if %errorlevel%==0 (
    set "TARGET_FILE=%~1"
) else (
    rem set "TARGET_FILE=%ROOT_DIR%\%~1"
    set "TARGET_FILE=%~1"
)

REM ファイル存在確認
if not exist "%TARGET_FILE%" (
    echo [ERROR] ファイルが存在しません: %TARGET_FILE%
    exit /b 1
)

REM 読み込み実行
type "%TARGET_FILE%"

endlocal
