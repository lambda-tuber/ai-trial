import pytest
from unittest.mock import Mock, MagicMock, patch
from pvv_mcp_server.ymm_avatar.mod_ymm_right_click_context_menu import ymm_right_click_context_menu


class TestYmmRightClickContextMenu:
    """ymm_right_click_context_menu関数のテストクラス"""
    
    @patch('pvv_mcp_server.ymm_avatar.mod_ymm_right_click_context_menu.QMenu')
    def test_context_menu_creation(self, mock_qmenu):
        """コンテキストメニューが作成されることを確認"""
        mock_self = Mock()
        mock_self.anime_types = ["stand", "mouth"]
        mock_self.anime_key = "stand"
        mock_self.position = "left_out"
        mock_self.flip = False
        mock_self.follow_enabled = True
        mock_self.mapToGlobal = Mock(return_value=Mock())
        
        mock_menu_instance = MagicMock()
        mock_qmenu.return_value = mock_menu_instance
        
        position = Mock()
        
        # メニュー表示
        ymm_right_click_context_menu(mock_self, position)
        
        # メニューが作成されたことを確認
        mock_qmenu.assert_called_once_with(mock_self)
        mock_menu_instance.exec.assert_called_once()
