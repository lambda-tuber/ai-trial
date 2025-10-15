# pvv_mcp_server/ymm_avatar/mod_ymm_right_click_context_menu.py 完全版

"""
YMMアバター右クリックメニューモジュール
"""
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import QPoint


def ymm_right_click_context_menu(self, mouse_position: QPoint) -> None:
    """
    右クリックメニューを表示
    
    Args:
        self: YmmAvatarWindowのインスタンス
        mouse_position: クリック位置
    """
    menu = QMenu(self)
    
    # アニメーションタイプ選択サブメニュー
    animation_menu = menu.addMenu("アニメーション")
    
    for anime_type in self.anime_types:
        # 各アニメタイプにサブメニューを作成
        type_submenu = animation_menu.addMenu(anime_type)
        
        # チェックマーク表示(現在選択中かどうか)
        if self.anime_key == anime_type:
            type_submenu.setTitle(f"✓ {anime_type}")
        
        # 選択アクション
        select_action = QAction("選択", self)
        select_action.triggered.connect(lambda checked=False, key=anime_type: self.set_anime_key(key))
        type_submenu.addAction(select_action)
        
        # 編集アクション(ダイアログを開く)
        edit_action = QAction("画像編集...", self)
        edit_action.triggered.connect(lambda checked=False, key=anime_type: self.ymm_dialogs[key].show())
        type_submenu.addAction(edit_action)
    
    menu.addSeparator()
    
    # アニメーション速度サブメニュー
    speed_menu = menu.addMenu("アニメーション速度")
    
    speeds = [
        ("超々高速 (25ms)", 25),
        ("超高速 (50ms)", 50),
        ("高速 (100ms)", 100),
        ("通常 (150ms)", 150),
        ("低速 (200ms)", 200),
        ("超低速 (250ms)", 250),
        ("超々低速 (300ms)", 300)
    ]
    
    current_speed = getattr(self, 'frame_timer_interval', 150)
    
    for label, speed_ms in speeds:
        action = QAction(label, self)
        action.setCheckable(True)
        action.setChecked(current_speed == speed_ms)
        action.triggered.connect(lambda checked=False, key=speed_ms: self.set_frame_timer_interval(key))
        speed_menu.addAction(action)
    
    menu.addSeparator()
    
    # 表示位置選択サブメニュー
    position_menu = menu.addMenu("表示位置")
    
    positions = [
        ("左下外側", "left_out"),
        ("左下中央", "left_center"),
        ("左下内側", "left_in"),
        ("右下内側", "right_in"),
        ("右下中央", "right_center"),
        ("右下外側", "right_out")
    ]
    
    current_position = getattr(self, 'position', 'left_out')
    
    for label, pos_key in positions:
        action = QAction(label, self)
        action.setCheckable(True)
        action.setChecked(current_position == pos_key)
        action.triggered.connect(lambda checked=False, key=pos_key: self.set_position(key))
        position_menu.addAction(action)
    
    menu.addSeparator()
    
    # 左右反転
    flip_action = QAction("左右反転", self)
    flip_action.setCheckable(True)
    flip_action.setChecked(self.flip)
    flip_action.triggered.connect(lambda checked: self.set_flip(checked))
    menu.addAction(flip_action)
    
    menu.addSeparator()
    
    # スケール選択サブメニュー
    scale_menu = menu.addMenu("スケール")
    
    scales = [
        ("25%", 25),
        ("50%", 50),
        ("75%", 75),
        ("100%", 100),
        ("125%", 125),
        ("150%", 150),
        ("175%", 175),
        ("200%", 200)
    ]
    
    current_scale = getattr(self, 'scale', 50)
    
    for label, pos_key in scales:
        action = QAction(label, self)
        action.setCheckable(True)
        action.setChecked(current_scale == pos_key)
        action.triggered.connect(lambda checked=False, key=pos_key: self.set_scale(key))
        scale_menu.addAction(action)
    
    menu.addSeparator()

    # 位置追随設定
    follow_menu = menu.addMenu("位置追随")
    
    follow_on_action = QAction("ON", self)
    follow_on_action.setCheckable(True)
    follow_on_action.setChecked(self.follow_timer.isActive())
    follow_on_action.triggered.connect(lambda: self.follow_timer.start())
    follow_menu.addAction(follow_on_action)
    
    follow_off_action = QAction("OFF", self)
    follow_off_action.setCheckable(True)
    follow_off_action.setChecked(not self.follow_timer.isActive())
    follow_off_action.triggered.connect(lambda: self.follow_timer.stop())
    follow_menu.addAction(follow_off_action)
    
    menu.addSeparator()
    
    # メニューを表示
    menu.exec(self.mapToGlobal(mouse_position))
