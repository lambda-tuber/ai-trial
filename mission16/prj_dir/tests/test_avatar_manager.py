"""
test_avatar_manager.py
mod_avatar_manager モジュールのユニットテスト
"""
import pytest
from unittest.mock import MagicMock, patch, call
from PySide6.QtWidgets import QApplication
import sys
import json

from pvv_mcp_server import mod_avatar_manager
from pvv_mcp_server.avatar.mod_avatar import AvatarWindow


class TestAvatarManager:
    """mod_avatar_manager のテストクラス"""
    
    @pytest.fixture(autouse=True)
    def reset_globals(self):
        """各テスト前にグローバル変数をリセット"""
        mod_avatar_manager._avatar = None
        mod_avatar_manager._avatars = None
        mod_avatar_manager._avatar_cache = {}
        yield
        mod_avatar_manager._avatar = None
        mod_avatar_manager._avatars = None
        mod_avatar_manager._avatar_cache = {}
    
    @pytest.fixture
    def qapp(self):
        """QApplicationのフィクスチャ"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        yield app
    
    def test_setup_enabled(self, qapp):
        """setup関数: アバター有効時の初期化テスト"""
        test_config = {
            "enabled": True,
            "avatars": {
                2: {
                    "話者": "四国めたん",
                    "表示": True,
                    "画像": {"立ち絵": ["image1.png"], "口パク": ["image2.png"]},
                    "反転": False,
                    "縮尺": 50,
                    "位置": "right_out"
                }
            }
        }
        
        with patch('pvv_mcp_server.mod_avatar_manager.get_avatar') as mock_get_avatar:
            mod_avatar_manager.setup(test_config)
            
            # グローバル変数が設定されたことを確認
            assert mod_avatar_manager._avatar == test_config
            assert mod_avatar_manager._avatars == test_config["avatars"]
            
            # get_avatarが呼ばれたことを確認
            mock_get_avatar.assert_called_once_with(2, True)
    
    def test_setup_disabled(self):
        """setup関数: アバター無効時の初期化テスト"""
        test_config = {
            "enabled": False,
            "avatars": {}
        }
        
        with patch('pvv_mcp_server.mod_avatar_manager.get_avatar') as mock_get_avatar:
            mod_avatar_manager.setup(test_config)
            
            # グローバル変数は設定されるが、get_avatarは呼ばれない
            assert mod_avatar_manager._avatar == test_config
            mock_get_avatar.assert_not_called()
    
    def test_set_anime_key_enabled(self):
        """set_anime_key関数: アバター有効時のテスト"""
        mod_avatar_manager._avatar = {"enabled": True}
        mod_avatar_manager._avatars = {2: {"話者": "四国めたん"}}
        
        mock_avatar = MagicMock()
        
        with patch('pvv_mcp_server.mod_avatar_manager.get_avatar', return_value=mock_avatar):
            mod_avatar_manager.set_anime_key(2, "口パク")
            
            mock_avatar.set_anime_key.assert_called_once_with("口パク")
    
    def test_set_anime_key_disabled(self):
        """set_anime_key関数: アバター無効時のテスト"""
        mod_avatar_manager._avatar = {"enabled": False}
        
        with patch('pvv_mcp_server.mod_avatar_manager.get_avatar') as mock_get_avatar:
            mod_avatar_manager.set_anime_key(2, "口パク")
            
            # アバター無効なので何もしない
            mock_get_avatar.assert_not_called()
    
    def test_get_avatar_from_cache(self, qapp):
        """get_avatar関数: キャッシュから取得するテスト"""
        avatar_conf = {
            "話者": "四国めたん",
            "画像": {"立ち絵": ["img1.png"], "口パク": ["img2.png"]},
            "反転": False,
            "縮尺": 50,
            "位置": "right_out"
        }
        
        mod_avatar_manager._avatar = {"enabled": True}
        mod_avatar_manager._avatars = {2: avatar_conf}
        
        # 実際のキャッシュキーを生成
        cache_key = json.dumps(avatar_conf, sort_keys=True)
        
        # キャッシュにモックインスタンスを設定
        mock_instance = MagicMock(spec=AvatarWindow)
        mod_avatar_manager._avatar_cache[cache_key] = mock_instance
        
        with patch('pvv_mcp_server.mod_avatar_manager.show_widget') as mock_show, \
             patch('pvv_mcp_server.mod_avatar_manager.get_images'):
            result = mod_avatar_manager.get_avatar(2, True)
            
            # キャッシュから取得されたことを確認
            assert result == mock_instance
            mock_show.assert_called_once_with(mock_instance)
    
    def test_get_avatar_create_new(self, qapp):
        """get_avatar関数: 新規作成のテスト"""
        mod_avatar_manager._avatar = {"enabled": True, "target": "Claude"}
        mod_avatar_manager._avatars = {
            2: {
                "話者": "四国めたん",
                "画像": {"立ち絵": ["img1.png"], "口パク": ["img2.png"]},
                "反転": False,
                "縮尺": 50,
                "位置": "right_out"
            }
        }
        
        with patch('pvv_mcp_server.mod_avatar_manager.get_images') as mock_get_images, \
             patch('pvv_mcp_server.mod_avatar_manager.AvatarWindow') as mock_avatar_window:
            
            mock_images = {"立ち絵": ["img1.png"], "口パク": ["img2.png"]}
            mock_get_images.return_value = mock_images
            
            mock_instance = MagicMock(spec=AvatarWindow)
            mock_avatar_window.return_value = mock_instance
            
            result = mod_avatar_manager.get_avatar(2, True)
            
            # AvatarWindowが正しいパラメータで作成されたことを確認
            mock_avatar_window.assert_called_once_with(
                mock_images,
                default_anime_key="立ち絵",
                flip=False,
                scale_percent=50,
                app_title="Claude",
                position="right_out"
            )
            
            # show/hideが呼ばれたことを確認
            mock_instance.update_position.assert_called_once()
            mock_instance.show.assert_called_once()
            
            # キャッシュに追加されたことを確認
            assert len(mod_avatar_manager._avatar_cache) == 1
            assert result == mock_instance
    
    def test_get_avatar_create_invisible(self, qapp):
        """get_avatar関数: 非表示で作成するテスト"""
        mod_avatar_manager._avatar = {"enabled": True, "target": "Claude"}
        mod_avatar_manager._avatars = {
            2: {
                "話者": "四国めたん",
                "画像": {"立ち絵": ["img1.png"], "口パク": ["img2.png"]},
                "反転": False,
                "縮尺": 50,
                "位置": "right_out"
            }
        }
        
        with patch('pvv_mcp_server.mod_avatar_manager.get_images') as mock_get_images, \
             patch('pvv_mcp_server.mod_avatar_manager.AvatarWindow') as mock_avatar_window:
            
            mock_images = {"立ち絵": ["img1.png"], "口パク": ["img2.png"]}
            mock_get_images.return_value = mock_images
            
            mock_instance = MagicMock(spec=AvatarWindow)
            mock_avatar_window.return_value = mock_instance
            
            result = mod_avatar_manager.get_avatar(2, False)
            
            # show/hideが正しく呼ばれたことを確認
            mock_instance.show.assert_called_once()
            mock_instance.hide.assert_called_once()
    
    def test_get_avatar_disabled(self):
        """get_avatar関数: アバター無効時のテスト"""
        mod_avatar_manager._avatar = {"enabled": False}
        
        result = mod_avatar_manager.get_avatar(2, True)
        
        # 無効時はNoneを返す
        assert result is None
    
    def test_get_images_with_existing_images(self):
        """get_images関数: 画像が既に設定されている場合"""
        images = {
            "立ち絵": ["custom_image1.png"],
            "口パク": ["custom_image2.png"]
        }
        
        result = mod_avatar_manager.get_images("四国めたん", images)
        
        # そのまま返される
        assert result == images
    
    def test_get_images_with_speaker_info(self):
        """get_images関数: speaker_infoから取得する場合"""
        images = {}
        
        with patch('pvv_mcp_server.mod_avatar_manager.speaker_info') as mock_speaker_info:
            mock_speaker_info.return_value = {"portrait": "base64encodedimage"}
            
            result = mod_avatar_manager.get_images("四国めたん", images)
            
            # portraitが設定されたことを確認
            assert result["立ち絵"] == ["base64encodedimage"]
            assert result["口パク"] == ["base64encodedimage"]
            mock_speaker_info.assert_called_once_with("四国めたん")
    
    def test_get_images_no_portrait(self):
        """get_images関数: portraitが取得できない場合"""
        images = {"test_key": ["test_value"]}
        
        with patch('pvv_mcp_server.mod_avatar_manager.speaker_info') as mock_speaker_info:
            mock_speaker_info.return_value = {}
            
            result = mod_avatar_manager.get_images("四国めたん", images)
            
            # 元の辞書の内容が返される
            assert result == images
    
    def test_show_widget(self, qapp):
        """show_widget関数: QMetaObject.invokeMethodが呼ばれることを確認"""
        mock_instance = MagicMock()
        
        with patch('pvv_mcp_server.mod_avatar_manager.QMetaObject.invokeMethod') as mock_invoke:
            mod_avatar_manager.show_widget(mock_instance)
            
            # invokeMethodが正しく呼ばれたことを確認
            assert mock_invoke.call_count == 1
            call_args = mock_invoke.call_args
            assert call_args[0][0] == mock_instance
            assert call_args[0][1] == "showWindow"