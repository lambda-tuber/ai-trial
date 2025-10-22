"""
test_load_image.py
mod_load_imageのユニットテスト
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
import zipfile
import io
from collections import defaultdict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pvv_mcp_server.avatar.mod_load_image import (
    load_image,
    _load_local_zip,
    _load_zip_from_url,
    _load_folder,
    _load_voicevox_portrait,
    _create_empty_zip_data
)


class TestLoadImage:
    """load_image関数のテストクラス"""
    
    def test_load_image_portrait(self):
        """portraitを指定した場合のテスト"""
        with patch('pvv_mcp_server.avatar.mod_load_image._load_voicevox_portrait') as mock_load:
            mock_load.return_value = {"他": {"portrait.png": b"test"}}
            
            result = load_image("portrait", speaker_id="test_speaker")
            
            mock_load.assert_called_once_with("test_speaker")
            assert "他" in result
    
    def test_load_image_url_zip(self):
        """URL(ZIP)を指定した場合のテスト"""
        with patch('pvv_mcp_server.avatar.mod_load_image._load_zip_from_url') as mock_load:
            mock_load.return_value = {"口": {"test.png": b"test"}}
            
            result = load_image("https://example.com/test.zip")
            
            mock_load.assert_called_once()
            assert "口" in result
    
    def test_load_image_folder(self):
        """フォルダを指定した場合のテスト"""
        with patch('pvv_mcp_server.avatar.mod_load_image._load_folder') as mock_load:
            with patch('os.path.isdir', return_value=True):
                mock_load.return_value = {"顔": {"test.png": b"test"}}
                
                result = load_image("C:\\test\\folder")
                
                mock_load.assert_called_once()
                assert "顔" in result
    
    def test_load_image_local_zip(self):
        """ローカルZIPを指定した場合のテスト"""
        with patch('pvv_mcp_server.avatar.mod_load_image._load_local_zip') as mock_load:
            mock_load.return_value = {"目": {"test.png": b"test"}}
            
            result = load_image("C:\\test\\file.zip")
            
            mock_load.assert_called_once()
            assert "目" in result
    
    def test_load_image_unknown_format(self):
        """不明な形式を指定した場合のテスト"""
        with patch('os.path.isdir', return_value=False):
            result = load_image("unknown_format")
            
            # 空のzip_dataが返されることを確認
            assert isinstance(result, defaultdict)


class TestLoadLocalZip:
    """_load_local_zip関数のテストクラス"""
    
    def test_load_local_zip_success(self):
        """正常にZIPファイルを読み込むテスト"""
        # ZIPファイルの内容をモック
        zip_content = io.BytesIO()
        with zipfile.ZipFile(zip_content, 'w') as zf:
            zf.writestr("test/口/test.png", b"test_image_data")
        
        zip_bytes = zip_content.getvalue()
        
        with patch('builtins.open', mock_open(read_data=zip_bytes)):
            parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
            result = _load_local_zip("test.zip", parts_folder)
            
            assert "口" in result
            assert "test.png" in result["口"]
            assert result["口"]["test.png"] == b"test_image_data"
    
    def test_load_local_zip_file_not_found(self):
        """ZIPファイルが存在しない場合のテスト"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
            result = _load_local_zip("nonexistent.zip", parts_folder)
            
            # 空のzip_dataが返されることを確認
            assert isinstance(result, defaultdict)
    
    def test_load_local_zip_invalid_category(self):
        """未知のカテゴリがある場合のテスト"""
        zip_content = io.BytesIO()
        with zipfile.ZipFile(zip_content, 'w') as zf:
            zf.writestr("test/未知/test.png", b"test_image_data")
        
        zip_bytes = zip_content.getvalue()
        
        with patch('builtins.open', mock_open(read_data=zip_bytes)):
            parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
            result = _load_local_zip("test.zip", parts_folder)
            
            # 未知のカテゴリは「他」に分類される
            assert "他" in result


class TestLoadZipFromUrl:
    """_load_zip_from_url関数のテストクラス"""
    
    def test_load_zip_from_url_success(self):
        """正常にURLからZIPを読み込むテスト"""
        # ZIPファイルの内容をモック
        zip_content = io.BytesIO()
        with zipfile.ZipFile(zip_content, 'w') as zf:
            zf.writestr("test/目/test.png", b"test_image_data")
        
        zip_bytes = zip_content.getvalue()
        
        mock_response = MagicMock()
        mock_response.read.return_value = zip_bytes
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        
        with patch('urllib.request.urlopen', return_value=mock_response):
            parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
            result = _load_zip_from_url("https://example.com/test.zip", parts_folder)
            
            assert "目" in result
            assert "test.png" in result["目"]
    
    def test_load_zip_from_url_network_error(self):
        """ネットワークエラーが発生した場合のテスト"""
        with patch('urllib.request.urlopen', side_effect=Exception("Network error")):
            parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
            result = _load_zip_from_url("https://example.com/test.zip", parts_folder)
            
            # 空のzip_dataが返されることを確認
            assert isinstance(result, defaultdict)
    
    def test_load_zip_from_url_japanese_path(self):
        """日本語を含むURLの場合のテスト"""
        zip_content = io.BytesIO()
        with zipfile.ZipFile(zip_content, 'w') as zf:
            zf.writestr("test/口/test.png", b"test_image_data")
        
        zip_bytes = zip_content.getvalue()
        
        mock_response = MagicMock()
        mock_response.read.return_value = zip_bytes
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        
        with patch('urllib.request.urlopen', return_value=mock_response):
            parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
            result = _load_zip_from_url("https://example.com/テスト.zip", parts_folder)
            
            # エラーなく処理されることを確認
            assert isinstance(result, defaultdict)


class TestLoadFolder:
    """_load_folder関数のテストクラス"""
    
    def test_load_folder_success(self):
        """正常にフォルダからPNGを読み込むテスト"""
        # モックファイルシステム
        mock_png_file = MagicMock()
        mock_png_file.name = "test.png"
        mock_png_file.parent.name = "口"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.rglob', return_value=[mock_png_file]):
                with patch('builtins.open', mock_open(read_data=b"test_image_data")):
                    parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
                    result = _load_folder("C:\\test\\folder", parts_folder)
                    
                    assert "口" in result
                    assert "test.png" in result["口"]
    
    def test_load_folder_not_exists(self):
        """フォルダが存在しない場合のテスト"""
        with patch('pathlib.Path.exists', return_value=False):
            parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
            result = _load_folder("C:\\nonexistent\\folder", parts_folder)
            
            # 空のzip_dataが返されることを確認
            assert isinstance(result, defaultdict)
    
    def test_load_folder_no_png_files(self):
        """PNGファイルがない場合のテスト"""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.rglob', return_value=[]):
                parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
                result = _load_folder("C:\\test\\folder", parts_folder)
                
                # 空のzip_dataが返されることを確認
                assert isinstance(result, defaultdict)
    
    def test_load_folder_invalid_category(self):
        """未知のカテゴリのフォルダがある場合のテスト"""
        mock_png_file = MagicMock()
        mock_png_file.name = "test.png"
        mock_png_file.parent.name = "未知カテゴリ"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.rglob', return_value=[mock_png_file]):
                with patch('builtins.open', mock_open(read_data=b"test_image_data")):
                    parts_folder = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
                    result = _load_folder("C:\\test\\folder", parts_folder)
                    
                    # 未知のカテゴリは「他」に分類される
                    assert "他" in result


class TestLoadVoicevoxPortrait:
    """_load_voicevox_portrait関数のテストクラス"""
    
    def test_load_voicevox_portrait_success(self):
        """正常にVOICEVOXポートレートを読み込むテスト"""
        mock_speaker_info = {
            "portrait": "https://example.com/portrait.png"
        }
        
        mock_response = MagicMock()
        mock_response.read.return_value = b"portrait_image_data"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        
        with patch('pvv_mcp_server.avatar.mod_load_image.speaker_info', return_value=mock_speaker_info):
            with patch('urllib.request.urlopen', return_value=mock_response):
                result = _load_voicevox_portrait("test_speaker")
                
                assert "他" in result
                assert "portrait.png" in result["他"]
                assert result["他"]["portrait.png"] == b"portrait_image_data"
    
    def test_load_voicevox_portrait_no_speaker_id(self):
        """speaker_idが指定されていない場合のテスト"""
        result = _load_voicevox_portrait(None)
        
        # 空のzip_dataが返されることを確認
        assert isinstance(result, defaultdict)
    
    def test_load_voicevox_portrait_no_portrait_url(self):
        """ポートレートURLが取得できない場合のテスト"""
        mock_speaker_info = {}
        
        with patch('pvv_mcp_server.avatar.mod_load_image.speaker_info', return_value=mock_speaker_info):
            result = _load_voicevox_portrait("test_speaker")
            
            # 空のzip_dataが返されることを確認
            assert isinstance(result, defaultdict)
    
    def test_load_voicevox_portrait_network_error(self):
        """ネットワークエラーが発生した場合のテスト"""
        mock_speaker_info = {
            "portrait": "https://example.com/portrait.png"
        }
        
        with patch('pvv_mcp_server.avatar.mod_load_image.speaker_info', return_value=mock_speaker_info):
            with patch('urllib.request.urlopen', side_effect=Exception("Network error")):
                result = _load_voicevox_portrait("test_speaker")
                
                # 空のzip_dataが返されることを確認
                assert isinstance(result, defaultdict)


class TestCreateEmptyZipData:
    """_create_empty_zip_data関数のテストクラス"""
    
    def test_create_empty_zip_data(self):
        """空のzip_dataが正しく作成されることをテスト"""
        result = _create_empty_zip_data()
        
        # defaultdictであることを確認
        assert isinstance(result, defaultdict)
        
        # 各カテゴリが存在することを確認
        expected_categories = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
        for cat in expected_categories:
            assert cat in result
            assert isinstance(result[cat], dict)
            assert len(result[cat]) == 0