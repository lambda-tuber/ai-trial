@echo off
chcp 65001 >nul
echo ============================================
echo   プロジェクトステータス確認ツール
echo ============================================
echo.

echo [1] プロジェクトフォルダ構造
echo --------------------------------------------
tree C:\work\lambda-tuber\ai-trial\mission18 /F /A
echo.

echo [2] リソースリスト
echo --------------------------------------------
type C:\work\lambda-tuber\ai-trial\mission18\pty-mcp-server\resources\resources-list.json
echo.

echo [3] プロンプトリスト
echo --------------------------------------------
type C:\work\lambda-tuber\ai-trial\mission18\pty-mcp-server\prompts\prompts-list.json
echo.

echo [4] ツールリスト
echo --------------------------------------------
type C:\work\lambda-tuber\ai-trial\mission18\pty-mcp-server\tools\tools-list.json
echo.

echo ============================================
echo   ステータス確認完了
echo ============================================
pause
