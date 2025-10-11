"""
mod_update_position.py
アバターウィンドウの位置を更新するモジュール (DPI Aware対応)
"""

import ctypes
from ctypes import wintypes
import logging
import sys

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# stderrへの出力ハンドラー
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Win32 API定義
user32 = ctypes.windll.user32

class RECT(ctypes.Structure):
    _fields_ = [
        ('left', wintypes.LONG),
        ('top', wintypes.LONG),
        ('right', wintypes.LONG),
        ('bottom', wintypes.LONG)
    ]


# DPI Awareを設定するフラグ (モジュールレベルで管理)
_dpi_aware_set = False


def set_process_dpi_aware():
    """
    プロセスをDPI Awareに設定
    これにより、Win32 APIとQt/PySide6で同じ座標系を使用できる
    
    Note:
        この関数は最初のウィンドウ作成前に一度だけ呼ぶ必要がある
    """
    global _dpi_aware_set
    
    if _dpi_aware_set:
        return
    
    try:
        # Windows Vista以降で利用可能
        user32.SetProcessDPIAware()
        logger.info("SetProcessDPIAware() called successfully")
        _dpi_aware_set = True
    except Exception as e:
        logger.warning(f"Failed to set process DPI aware: {e}")


def find_window_by_title(title: str):
    """
    ウィンドウタイトルからHWNDを取得
    
    Args:
        title: 検索するウィンドウタイトル(部分一致)
    
    Returns:
        HWND: ウィンドウハンドル(見つからない場合はNone)
    """
    def enum_windows_callback(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                window_title = buffer.value
                
                if title in window_title:
                    # 見つかったHWNDをリストに追加
                    found_windows.append(hwnd)
        return True
    
    found_windows = []
    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
    
    return found_windows[0] if found_windows else None


def get_window_rect(hwnd) -> tuple:
    """
    Win32 APIを使用してウィンドウの位置とサイズを取得
    
    Args:
        hwnd: ウィンドウハンドル
    
    Returns:
        tuple: (x, y, width, height)
    """
    rect = RECT()
    if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        x = rect.left
        y = rect.top
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        return (x, y, width, height)
    else:
        raise Exception("GetWindowRect failed")


def update_position(self) -> None:
    """
    self.app_titleで指定されたアプリケーションウィンドウの指定位置に
    下揃えするように、self(AvatarWindow)を移動する
    
    Args:
        self: AvatarWindowのインスタンス
              - self.app_title: ターゲットアプリケーションのウィンドウタイトル
              - self.position: 表示位置 ("left_out", "left_in", "right_in", "right_out")
    
    Returns:
        None
    """
    # DPI Awareを設定 (初回のみ実行)
    set_process_dpi_aware()
    
    # app_titleが存在しない場合は何もしない
    if not hasattr(self, 'app_title') or not self.app_title:
        logger.warning("app_title is not set")
        return
    
    # positionが存在しない場合はデフォルト値を設定
    if not hasattr(self, 'position'):
        self.position = "left_out"
    
    try:
        # Win32 APIでターゲットウィンドウを検索
        hwnd = find_window_by_title(self.app_title)
        
        if not hwnd:
            logger.warning(f"Window with title '{self.app_title}' not found")
            return
        
        # Win32 APIでウィンドウの位置とサイズを取得
        target_x, target_y, target_width, target_height = get_window_rect(hwnd)
        logger.info(f"claude x,y w,h : {target_x}, {target_y}, {target_width}, {target_height}")
        
        # 自身のウィンドウサイズを取得
        avatar_width = self.width()
        avatar_height = self.height()
        
        logger.info(f"avatar w,h : {avatar_width}, {avatar_height}")

        # positionに応じて配置位置を計算
        if self.position == "left_out":
            # 左下外側(ターゲットウィンドウの左外側)
            new_x = target_x - avatar_width
            new_y = target_y + target_height - avatar_height
            
        elif self.position == "left_in":
            # 左下内側(ターゲットウィンドウの左内側)
            new_x = target_x
            new_y = target_y + target_height - avatar_height
            
        elif self.position == "right_in":
            # 右下内側(ターゲットウィンドウの右内側)
            new_x = target_x + target_width - avatar_width
            new_y = target_y + target_height - avatar_height
            
        elif self.position == "right_out":
            # 右下外側(ターゲットウィンドウの右外側)
            new_x = target_x + target_width
            new_y = target_y + target_height - avatar_height
            
        else:
            logger.warning(f"Unknown position: {self.position}")
            return
        
        # 現在の位置を取得してログ出力
        current_x = self.x()
        current_y = self.y()
        logger.info(f"current position: ({current_x}, {current_y})")
        logger.info(f"new position: ({new_x}, {new_y})")
        
        # ウィンドウを移動
        self.move(int(new_x), int(new_y))
        
    except Exception as e:
        logger.warning(f"Failed to update position: {e}")
    