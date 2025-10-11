"""
mod_update_position.py
アバターウィンドウの位置を更新するモジュール
"""

import pygetwindow as gw
import logging
import sys
import ctypes

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# stderrへの出力ハンドラー
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_windows_scaling() -> float:
    """
    現在のDPIスケールを取得（例: 1.25, 1.5）
    リモートデスクトップや高DPI環境での位置ずれ補正用
    """
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()  # DPI対応を有効化
        dpi = user32.GetDpiForSystem()
        return dpi / 96.0  # 96 DPI を基準にスケール計算
    except Exception as e:
        logger.warning(f"Failed to get DPI scaling: {e}")
        return 1.0

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
    # app_titleが存在しない場合は何もしない
    if not hasattr(self, 'app_title') or not self.app_title:
        logger.warning("app_title is not set")
        return
    
    # positionが存在しない場合はデフォルト値を設定
    if not hasattr(self, 'position'):
        self.position = "left_out"
    
    try:
        # ターゲットウィンドウを検索
        windows = gw.getWindowsWithTitle(self.app_title)
        
        if not windows:
            logger.warning(f"Window with title '{self.app_title}' not found")
            return
        
        # 最初に見つかったウィンドウを使用
        target_window = windows[0]
        
        # ターゲットウィンドウの位置とサイズを取得
        target_x = target_window.left
        target_y = target_window.top
        target_width = target_window.width
        target_height = target_window.height

        # DPIスケーリング取得
        scale = get_windows_scaling()

        # スケーリング補正
        target_x = int(target_x * scale)
        target_y = int(target_y * scale)
        target_width = int(target_width * scale)
        target_height = int(target_height * scale)
                
        # 自身のウィンドウサイズを取得
        avatar_width = self.width()
        avatar_height = self.height()
        
        # positionに応じて配置位置を計算
        if self.position == "left_out":
            # 左下外側（ターゲットウィンドウの左外側）
            new_x = target_x - avatar_width
            new_y = target_y + target_height - avatar_height
            
        elif self.position == "left_in":
            # 左下内側（ターゲットウィンドウの左内側）
            new_x = target_x
            new_y = target_y + target_height - avatar_height
            
        elif self.position == "right_in":
            # 右下内側（ターゲットウィンドウの右内側）
            new_x = target_x + target_width - avatar_width
            new_y = target_y + target_height - avatar_height
            
        elif self.position == "right_out":
            # 右下外側（ターゲットウィンドウの右外側）
            new_x = target_x + target_width
            new_y = target_y + target_height - avatar_height
            
        else:
            logger.warning(f"Unknown position: {self.position}")
            return
        
        # ウィンドウを移動
        self.move(int(new_x), int(new_y))
        
    except Exception as e:
        logger.warning(f"Failed to update position: {e}")
        