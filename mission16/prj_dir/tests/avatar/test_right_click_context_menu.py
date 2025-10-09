"""
test_right_click_context_menu.py
mod_right_click_context_menu.py のユニットテスト
"""

import pytest
from unittest.mock import MagicMock, patch, call
from PySide6.QtCore import QPoint, QTimer
from PySide6.QtWidgets import QMenu, QApplication
from PySide6.QtGui import QAction
import sys

# テスト対象のモジュールをインポート
from pvv_mcp_server.avatar.mod_right_click_context_menu import right_click_context_menu


class TestRightClickContextMenu:
    """right_click_context_menu関数のテストクラス"""
    
    @pytest.fixture
    def app(self):
        """QApplicationのセットアップ"""
        if not QApplication.instance():
            return QApplication(sys.argv)
        return QApplication.instance()
    
    @pytest.fixture
    def mock_avatar(self):
        """AvatarWindowのモックを作成"""
        mock = MagicMock()
        
        # 基本属性の設定
        mock.pixmap_dict = {
            "idle": [MagicMock(), MagicMock()],
            "talk": [MagicMock(), MagicMock(), MagicMock()]
        }
        mock.frame_timer_interval = 100
        mock.position = "left_out"
        mock.flip = False
        
        # follow_timerのモック
        mock.follow_timer = MagicMock(spec=QTimer)
        mock.follow_timer.isActive.return_value = True
        
        # メソッドのモック
        mock.set_anime_key = MagicMock()
        mock.set_frame_timer_interval = MagicMock()
        mock.set_position = MagicMock()
        mock.set_flip = MagicMock()
        mock.mapToGlobal = MagicMock(return_value=QPoint(100, 100))
        
        return mock
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_menu_creation(self, mock_qmenu_class, app, mock_avatar):
        """メニューが正しく作成されることを確認"""
        mock_menu = MagicMock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        position = QPoint(50, 50)
        right_click_context_menu(mock_avatar, position)
        
        # QMenuが作成されたことを確認
        mock_qmenu_class.assert_called_once_with(mock_avatar)
        
        # exec_が呼ばれたことを確認
        mock_menu.exec.assert_called_once()
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QAction')
    def test_animation_submenu_with_animations(self, mock_qaction_class, mock_qmenu_class, app, mock_avatar):
        """アニメーションサブメニューが正しく作成されることを確認"""
        mock_menu = MagicMock(spec=QMenu)
        mock_submenu = MagicMock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        mock_menu.addMenu.return_value = mock_submenu
        
        position = QPoint(50, 50)
        right_click_context_menu(mock_avatar, position)
        
        # アニメーションサブメニューが追加されたことを確認
        assert any("アニメーション" in str(call) for call in mock_menu.addMenu.call_args_list)
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_animation_submenu_without_animations(self, mock_qmenu_class, app, mock_avatar):
        """アニメーションが無い場合の処理を確認"""
        # pixmap_dictを空にする
        mock_avatar.pixmap_dict = {}
        
        mock_menu = MagicMock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        position = QPoint(50, 50)
        right_click_context_menu(mock_avatar, position)
        
        # メニューが作成されたことを確認
        mock_qmenu_class.assert_called_once_with(mock_avatar)
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_speed_submenu_creation(self, mock_qmenu_class, app, mock_avatar):
        """速度設定サブメニューが正しく作成されることを確認"""
        mock_menu = MagicMock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        position = QPoint(50, 50)
        right_click_context_menu(mock_avatar, position)
        
        # 速度サブメニューが追加されたことを確認
        assert any("速度" in str(call) for call in mock_menu.addMenu.call_args_list)
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_position_submenu_creation(self, mock_qmenu_class, app, mock_avatar):
        """表示位置サブメニューが正しく作成されることを確認"""
        mock_menu = MagicMock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        position = QPoint(50, 50)
        right_click_context_menu(mock_avatar, position)
        
        # 位置サブメニューが追加されたことを確認
        assert any("表示位置" in str(call) for call in mock_menu.addMenu.call_args_list)
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_flip_menu_creation(self, mock_qmenu_class, app, mock_avatar):
        """左右反転メニューが正しく作成されることを確認"""
        mock_menu = MagicMock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        position = QPoint(50, 50)
        right_click_context_menu(mock_avatar, position)
        
        # 左右反転アクションが追加されたことを確認
        assert mock_menu.addAction.called
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_follow_submenu_creation(self, mock_qmenu_class, app, mock_avatar):
        """位置追随サブメニューが正しく作成されることを確認"""
        mock_menu = MagicMock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        position = QPoint(50, 50)
        right_click_context_menu(mock_avatar, position)
        
        # 位置追随サブメニューが追加されたことを確認
        assert any("追随" in str(call) for call in mock_menu.addMenu.call_args_list)
    
    @patch('pvv_mcp_server.avatar.mod_right_click_context_menu.QMenu')
    def test_mapToGlobal_called(self, mock_qmenu_class, app, mock_avatar):
        """mapToGlobalが正しく呼ばれることを確認"""
        mock_menu = MagicMock(spec=QMenu)
        mock_qmenu_class.return_value = mock_menu
        
        position = QPoint(50, 50)
        right_click_context_menu(mock_avatar, position)
        
        # mapToGlobalが呼ばれたことを確認
        mock_avatar.mapToGlobal.assert_called_once_with(position)

        