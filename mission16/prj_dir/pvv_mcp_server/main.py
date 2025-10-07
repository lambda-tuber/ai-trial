"""
pvv-mcp-server のエントリポイント

MCPサーバを起動し、コマンドライン引数を処理する
"""
import argparse
import sys
from importlib.metadata import version, PackageNotFoundError

from pvv_mcp_server import mod_service


def get_version():
    """
    パッケージのバージョン情報を取得する
    
    Returns:
        str: バージョン文字列
    """
    try:
        return version("pvv-mcp-server")
    except PackageNotFoundError:
        return "development"


def main():
    """
    MCPサーバを起動する
    コマンドライン引数でバージョン表示にも対応
    """
    parser = argparse.ArgumentParser(
        description="VOICEVOX MCP Server - 音声合成機能を提供するMCPサーバ"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"pvv-mcp-server {get_version()}"
    )
    
    # 引数をパース（--version の場合はここで終了する）
    parser.parse_args()
    
    # MCPサーバを起動
    mod_service.start()


if __name__ == "__main__":
    main()