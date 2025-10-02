"""
MCP Server service module
MCPサーバクラスとToolsを定義する
"""
from mcp.server.fastmcp import FastMCP
from . import mod_speak_metan_aska

mcp = FastMCP("voicevox-mcp-server")

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


def start():
    """stdio モードで FastMCP を起動"""
    mcp.run(transport="stdio")
