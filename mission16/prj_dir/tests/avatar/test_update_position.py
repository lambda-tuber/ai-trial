"""
test_update_position.py
mod_update_positionのユニットテスト
"""

import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

# テスト対象モジュールのインポート
sys.path.insert(0, 'C:/work/lambda-tuber/ai-trial/mission16/prj_dir')
from pvv_mcp_server.avatar.mod_update_position import (
    update_position,
    find_window_by_title,
    get_window_rect,
    RECT
)


class MockAvatarWindow:
    """テスト用のAvatarWindowモック"""
    def __init__(self):
        self.app_title = "Claude"
        self.position = "left_out"
        self._width = 200
        self._height = 300
        self._x = 0
        self._y = 0
    
    def width(self):
        return self._width
    
    def height(self):
        return self._height
    
    def move(self, x, y):
        self._x = x
        self._y = y


class TestFindWindowByTitle:
    """find_window_by_title関数のテスト"""
    
    @patch('pvv_mcp_server.avatar.mod_update_position.user32')
    def test_find_window_success(self, mock_user32):
        """ウィンドウが見つかる場合のテスト"""
        # モックの設定
        mock_hwnd = 12345
        
        def mock_enum_windows(callback, lparam):
            # テスト用のウィンドウを列挙
            callback(mock_hwnd, lparam)
            return True
        
        mock_user32.EnumWindows.side_effect = mock_enum_windows
        mock_user32.IsWindowVisible.return_value = True
        mock_user32.GetWindowTextLengthW.return_value = 6
        mock_user32.GetWindowTextW.side_effect = lambda hwnd, buf, size: buf.__setitem__(slice(0, 6), "Claude")
        
        # 実行
        result = find_window_by_title("Claude")
        
        # 検証
        assert result == mock_hwnd
    
    @patch('pvv_mcp_server.avatar.mod_update_position.user32')
    def test_find_window_not_found(self, mock_user32):
        """ウィンドウが見つからない場合のテスト"""
        # モックの設定
        def mock_enum_windows(callback, lparam):
            # ウィンドウを列挙しない
            return True
        
        mock_user32.EnumWindows.side_effect = mock_enum_windows
        
        # 実行
        result = find_window_by_title("NonExistent")
        
        # 検証
        assert result is None


class TestGetWindowRect:
    """get_window_rect関数のテスト"""
    
    @patch('pvv_mcp_server.avatar.mod_update_position.user32.GetWindowRect')
    def test_get_window_rect_success(self, mock_get_window_rect):
        """正常にウィンドウ矩形を取得できる場合のテスト"""
        # モックの設定
        mock_hwnd = 12345
        
        # RECT構造体を実際に作成してテスト
        test_rect = RECT()
        test_rect.left = 100
        test_rect.top = 200
        test_rect.right = 900
        test_rect.bottom = 700
        
        def side_effect(hwnd, rect_ptr):
            # 実際のRECT構造体の値をコピー
            import ctypes
            ctypes.memmove(rect_ptr, ctypes.addressof(test_rect), ctypes.sizeof(RECT))
            return True
        
        mock_get_window_rect.side_effect = side_effect
        
        # 実行
        x, y, width, height = get_window_rect(mock_hwnd)
        
        # 検証
        assert x == 100
        assert y == 200
        assert width == 800
        assert height == 500
    
    @patch('pvv_mcp_server.avatar.mod_update_position.user32.GetWindowRect')
    def test_get_window_rect_failure(self, mock_get_window_rect):
        """ウィンドウ矩形取得に失敗する場合のテスト"""
        # モックの設定
        mock_hwnd = 12345
        mock_get_window_rect.return_value = False
        
        # 実行と検証
        with pytest.raises(Exception, match="GetWindowRect failed"):
            get_window_rect(mock_hwnd)


class TestUpdatePosition:
    """update_position関数のテスト"""
    
    @patch('pvv_mcp_server.avatar.mod_update_position.find_window_by_title')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_window_rect')
    def test_update_position_left_out(self, mock_get_rect, mock_find_window):
        """left_out位置の計算テスト"""
        # モックの設定
        mock_find_window.return_value = 12345
        mock_get_rect.return_value = (100, 200, 800, 500)  # x, y, width, height
        
        # テスト対象の準備
        avatar = MockAvatarWindow()
        avatar.position = "left_out"
        
        # 実行
        update_position(avatar)
        
        # 検証: x = 100 - 200 = -100, y = 200 + 500 - 300 = 400
        assert avatar._x == -100
        assert avatar._y == 400
    
    @patch('pvv_mcp_server.avatar.mod_update_position.find_window_by_title')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_window_rect')
    def test_update_position_left_in(self, mock_get_rect, mock_find_window):
        """left_in位置の計算テスト"""
        # モックの設定
        mock_find_window.return_value = 12345
        mock_get_rect.return_value = (100, 200, 800, 500)
        
        # テスト対象の準備
        avatar = MockAvatarWindow()
        avatar.position = "left_in"
        
        # 実行
        update_position(avatar)
        
        # 検証: x = 100, y = 200 + 500 - 300 = 400
        assert avatar._x == 100
        assert avatar._y == 400
    
    @patch('pvv_mcp_server.avatar.mod_update_position.find_window_by_title')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_window_rect')
    def test_update_position_right_in(self, mock_get_rect, mock_find_window):
        """right_in位置の計算テスト"""
        # モックの設定
        mock_find_window.return_value = 12345
        mock_get_rect.return_value = (100, 200, 800, 500)
        
        # テスト対象の準備
        avatar = MockAvatarWindow()
        avatar.position = "right_in"
        
        # 実行
        update_position(avatar)
        
        # 検証: x = 100 + 800 - 200 = 700, y = 200 + 500 - 300 = 400
        assert avatar._x == 700
        assert avatar._y == 400
    
    @patch('pvv_mcp_server.avatar.mod_update_position.find_window_by_title')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_window_rect')
    def test_update_position_right_out(self, mock_get_rect, mock_find_window):
        """right_out位置の計算テスト"""
        # モックの設定
        mock_find_window.return_value = 12345
        mock_get_rect.return_value = (100, 200, 800, 500)
        
        # テスト対象の準備
        avatar = MockAvatarWindow()
        avatar.position = "right_out"
        
        # 実行
        update_position(avatar)
        
        # 検証: x = 100 + 800 = 900, y = 200 + 500 - 300 = 400
        assert avatar._x == 900
        assert avatar._y == 400
    
    @patch('pvv_mcp_server.avatar.mod_update_position.find_window_by_title')
    def test_update_position_window_not_found(self, mock_find_window):
        """ウィンドウが見つからない場合のテスト"""
        # モックの設定
        mock_find_window.return_value = None
        
        # テスト対象の準備
        avatar = MockAvatarWindow()
        initial_x = avatar._x
        initial_y = avatar._y
        
        # 実行
        update_position(avatar)
        
        # 検証: 位置が変更されないこと
        assert avatar._x == initial_x
        assert avatar._y == initial_y
    
    def test_update_position_no_app_title(self):
        """app_titleが設定されていない場合のテスト"""
        # テスト対象の準備
        avatar = MockAvatarWindow()
        avatar.app_title = None
        initial_x = avatar._x
        initial_y = avatar._y
        
        # 実行
        update_position(avatar)
        
        # 検証: 位置が変更されないこと
        assert avatar._x == initial_x
        assert avatar._y == initial_y
    
    @patch('pvv_mcp_server.avatar.mod_update_position.find_window_by_title')
    @patch('pvv_mcp_server.avatar.mod_update_position.get_window_rect')
    def test_update_position_default_position(self, mock_get_rect, mock_find_window):
        """positionが設定されていない場合のデフォルト値テスト"""
        # モックの設定
        mock_find_window.return_value = 12345
        mock_get_rect.return_value = (100, 200, 800, 500)
        
        # テスト対象の準備
        avatar = MockAvatarWindow()
        delattr(avatar, 'position')  # positionを削除
        
        # 実行
        update_position(avatar)
        
        # 検証: デフォルトのleft_outとして動作
        assert avatar.position == "left_out"
        assert avatar._x == -100
        assert avatar._y == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

    