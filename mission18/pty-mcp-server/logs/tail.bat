@echo off
REM --- コンソールを UTF-8 に切り替え ---
chcp 65001 >nul

REM --- 現在のユーザー名を取得 ---
set USERNAME=%USERNAME%

REM --- ログファイル名を引数で受け取る ---
REM --- 省略時はデフォルトログファイル ---
if "%1"=="" (
    set LOGFILE=C:\Users\%USERNAME%\AppData\Roaming\Claude\logs\mcp-server-pty-mcp-server.log
) else (
    set LOGFILE=%1
)

REM --- PowerShell で tail 実行 ---
powershell -NoLogo -NoExit -ExecutionPolicy Bypass -Command "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; Get-Content \"%LOGFILE%\" -Wait -Tail 20 -Encoding UTF8"
