"""
test_update_frame.py
mod_update_frame.pyのユニットテスト
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtGui import QPixmap

# テスト対象モジュールのインポート
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pvv_mcp_server', 'avatar'))
from pvv_mcp_server.avatar.mod_update_frame import update_frame


class TestUpdateFrame:
    """update_frame関数のテストクラス"""
    
    @pytest.fixture(scope="class")
    def qapp(self):
        """QApplicationインスタンスを作成（GUIテストに必要）"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
    
    @pytest.fixture
    def mock_self(self, qapp):
        """AvatarWindowのモックインスタンス"""
        mock = Mock(spec=QWidget)
        
        # QLabel のモック
        mock.label = Mock(spec=QLabel)
        mock.label.setPixmap = MagicMock()
        
        # テスト用のQPixmapを作成
        pixmap1 = QPixmap(100, 100)
        pixmap2 = QPixmap(100, 100)
        pixmap3 = QPixmap(100, 100)
        
        # pixmap_dictの設定
        mock.pixmap_dict = {
            "idle": [pixmap1, pixmap2, pixmap3],
            "talk": [pixmap1, pixmap2]
        }
        
        # 初期アニメーションキーとインデックス
        mock.anime_key = "idle"
        mock.anime_index = 0
        
        return mock
    
    def test_update_frame_basic(self, mock_self):
        """基本的なフレーム更新のテスト"""
        # 初期状態
        assert mock_self.anime_index == 0
        
        # フレーム更新
        update_frame(mock_self)
        
        # setPixmapが呼ばれたか確認
        mock_self.label.setPixmap.assert_called_once()
        
        # インデックスがインクリメントされたか確認
        assert mock_self.anime_index == 1
    
    def test_update_frame_loop(self, mock_self):
        """フレームのループ動作テスト"""
        mock_self.anime_key = "idle"
        mock_self.anime_index = 0
        
        # 3回更新（idleは3フレーム）
        update_frame(mock_self)
        assert mock_self.anime_index == 1
        
        update_frame(mock_self)
        assert mock_self.anime_index == 2
        
        update_frame(mock_self)
        # ループして0に戻る
        assert mock_self.anime_index == 0
    
    def test_update_frame_different_animation(self, mock_self):
        """異なるアニメーションキーのテスト"""
        mock_self.anime_key = "talk"
        mock_self.anime_index = 0
        
        # 2回更新（talkは2フレーム）
        update_frame(mock_self)
        assert mock_self.anime_index == 1
        
        update_frame(mock_self)
        # ループして0に戻る
        assert mock_self.anime_index == 0
    
    def test_update_frame_no_pixmap_dict(self, mock_self):
        """pixmap_dictが存在しない場合のテスト"""
        delattr(mock_self, 'pixmap_dict')
        
        # エラーにならず、何もしない
        update_frame(mock_self)
        
        # setPixmapが呼ばれていないことを確認
        mock_self.label.setPixmap.assert_not_called()
    
    def test_update_frame_empty_pixmap_dict(self, mock_self):
        """pixmap_dictが空の場合のテスト"""
        mock_self.pixmap_dict = {}
        
        # エラーにならず、何もしない
        update_frame(mock_self)
        
        # setPixmapが呼ばれていないことを確認
        mock_self.label.setPixmap.assert_not_called()
    
    def test_update_frame_invalid_anime_key(self, mock_self):
        """無効なanime_keyの場合のテスト"""
        mock_self.anime_key = "nonexistent"
        
        # エラーにならず、何もしない
        update_frame(mock_self)
        
        # setPixmapが呼ばれていないことを確認
        mock_self.label.setPixmap.assert_not_called()
    
    def test_update_frame_no_anime_key(self, mock_self):
        """anime_keyが存在しない場合のテスト"""
        delattr(mock_self, 'anime_key')
        
        # エラーにならず、何もしない
        update_frame(mock_self)
        
        # setPixmapが呼ばれていないことを確認
        mock_self.label.setPixmap.assert_not_called()
    
    def test_update_frame_no_label(self, mock_self):
        """labelが存在しない場合のテスト"""
        delattr(mock_self, 'label')
        
        # エラーにならず、何もしない
        update_frame(mock_self)
    
    def test_update_frame_no_anime_index(self, mock_self):
        """anime_indexが存在しない場合のテスト（自動初期化）"""
        delattr(mock_self, 'anime_index')
        
        # anime_indexが自動的に0で初期化される
        update_frame(mock_self)
        
        # anime_indexが作成され、1になっている
        assert hasattr(mock_self, 'anime_index')
        assert mock_self.anime_index == 1
        
        # setPixmapが呼ばれたことを確認
        mock_self.label.setPixmap.assert_called_once()
    
    def test_update_frame_empty_pixmap_list(self, mock_self):
        """空のpixmap_listの場合のテスト"""
        mock_self.pixmap_dict = {"idle": []}
        mock_self.anime_key = "idle"
        
        # エラーにならず、何もしない
        update_frame(mock_self)
        
        # setPixmapが呼ばれていないことを確認
        mock_self.label.setPixmap.assert_not_called()
    
    def test_update_frame_single_frame(self, qapp):
        """1フレームのアニメーションのテスト"""
        mock = Mock(spec=QWidget)
        mock.label = Mock(spec=QLabel)
        mock.label.setPixmap = MagicMock()
        
        pixmap = QPixmap(100, 100)
        mock.pixmap_dict = {"idle": [pixmap]}
        mock.anime_key = "idle"
        mock.anime_index = 0
        
        # 1フレームでもループする
        update_frame(mock)
        assert mock.anime_index == 0  # 1 % 1 = 0
        
        update_frame(mock)
        assert mock.anime_index == 0  # 1 % 1 = 0
