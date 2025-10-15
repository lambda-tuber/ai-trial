import pytest
from unittest.mock import Mock, mock_open, patch
from pvv_mcp_server.ymm_avatar.mod_load_zip_data import load_zip_data


class TestLoadZipData:
    """load_zip_data関数のテストクラス"""
    
    def test_load_zip_data_success(self):
        """正常にZIPデータを読み込めることを確認"""
        # モックオブジェクト作成
        mock_self = Mock()
        mock_self.zip_data = None
        mock_self.zip_path = None
        
        zip_path = "test.zip"
        zip_content = b"fake zip data"
        
        # ファイル読み込みをモック
        with patch("builtins.open", mock_open(read_data=zip_content)):
            load_zip_data(mock_self, zip_path)
        
        # 検証
        assert mock_self.zip_data == zip_content
        assert mock_self.zip_path == zip_path
    
    def test_load_zip_data_file_not_found(self):
        """ファイルが見つからない場合のテスト"""
        mock_self = Mock()
        mock_self.zip_data = None
        mock_self.zip_path = None
        
        with patch("builtins.open", side_effect=FileNotFoundError()):
            load_zip_data(mock_self, "nonexistent.zip")
        
        # エラー時はNoneが設定される
        assert mock_self.zip_data is None
