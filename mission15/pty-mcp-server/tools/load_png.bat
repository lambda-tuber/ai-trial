@echo off
REM ======================================
REM PNGファイルをBase64に変換してJSON出力するバッチ
REM 標準出力: JSON
REM 標準エラー: echoメッセージ
REM 使い方: png_to_json.bat sample.png
REM ======================================

if "%~1"=="" (
    echo [ERROR] 使用方法: %~nx0 [PNGファイル] 1>&2
    exit /b 1
)

set "pngfile=%~1"

if not exist "%pngfile%" (
    echo [ERROR] ファイルが見つかりません: %pngfile% 1>&2
    exit /b 1
)

REM PowerShell で Base64 + JSON 作成
powershell -NoProfile -Command ^
  "$bytes = [System.IO.File]::ReadAllBytes('%pngfile%');" ^
  "$b64 = [Convert]::ToBase64String($bytes);" ^
  "$json = @{ type='image'; mime_type='image/png'; data=$b64 } | ConvertTo-Json -Compress;" ^
  "Write-Output $json"

echo [INFO] JSON出力完了: %pngfile% 1>&2
