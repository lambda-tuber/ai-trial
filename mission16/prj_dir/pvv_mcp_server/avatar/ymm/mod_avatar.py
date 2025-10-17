import sys
from PySide6.QtWidgets import QWidget, QLabel, QApplication
from PySide6.QtCore import Qt, QTimer, QPoint, Slot
from PySide6.QtGui import QPixmap, QShortcut, QKeySequence
from pvv_mcp_server.avatar.ymm.mod_load_zip import load_zip_data
from pvv_mcp_server.avatar.ymm.mod_update_frame import ymm_update_frame
from pvv_mcp_server.avatar.ymm.mod_right_click_context_menu import ymm_right_click_context_menu
from pvv_mcp_server.avatar.ymm.mod_avatar_dialog import YmmAvatarDialog
import pvv_mcp_server.avatar.mod_update_position
import logging

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


class YmmAvatarWindow(QWidget):
    """YMMアバター表示ウィンドウ"""
    
    def show(self):
        """show()をオーバーライドしてログ出力"""
        logger.info(f"YmmAvatarDialog.show() called. title={self.windowTitle()}")
        super().show()
        logger.info(f"YmmAvatarDialog.show() completed. isVisible={self.isVisible()}")

    def __init__(self, style_id, speaker_name, zip_path=None, app_title="Claude", anime_types=None, flip=False, scale_percent=100, position="right_out", config=None):
        """
        コンストラクタ
        
        Args:
            zip_path: YMM立ち絵ZIPファイルのパス
            app_title: 追随対象アプリケーションのウィンドウタイトル
            anime_types: アニメーションタイプのリスト (例: ["stand", "mouth"])
            flip: 左右反転フラグ
            scale_percent: 縮尺パーセント
            position: 表示位置 (left_out, left_in, right_in, right_out)
        """
        logger.info(f"YmmAvatarDialog.__init__ 開始: config={config is not None}")
        super().__init__()
        
        # 基本設定
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Escキーで非表示
        #QShortcut(QKeySequence("Escape"), self, self.hide)
        QShortcut(QKeySequence("Escape"), self, QApplication.quit)
        
        # UI初期化
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        
        # メンバ変数初期化
        self.style_id = style_id
        self.speaker_name = speaker_name
        self.zip_path = zip_path
        self.app_title = app_title
        self.position = position  # 表示位置: left_out, left_in, right_in, right_out
        self.flip = flip  # 左右反転
        self.scale_percent = scale_percent  # 縮尺パーセント
        self.anime_types = anime_types or ["立ち絵", "口パク"]
        self.frame_timer_interval = 50
        self.follow_timer_interval = 150
        
        # zip読み込み
        self.zip_data = load_zip_data(self.zip_path,  self.style_id)  # [パーツ][PNGファイル[バイナリデータ]

        # アニメーション設定
        self.anime_types = anime_types or ["立ち絵", "口パク"]
        self.anime_key = anime_types[0] if anime_types else "立ち絵"  # 現在のアニメーションタイプ
        
        # YMMダイアログ管理
        self.ymm_dialogs = {}
        for anime_type in self.anime_types:
            conf = None
            if config and "dialogs" in config and anime_type in config["dialogs"]:
                conf = config["dialogs"][anime_type]
            
            dialog = YmmAvatarDialog(self, anime_type, self.zip_data, self.scale_percent, self.flip, self.frame_timer_interval, conf)
            self.ymm_dialogs[anime_type] = dialog
            # ★ 初回show→hideで初期化(ウィンドウマネージャーに登録)
            #dialog.show()
            #QApplication.processEvents()  # イベント処理を強制
            #dialog.hide()

        # 初期表示
        ymm_update_frame(self)
        self.update_position()
        
        # タイマー設定
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(lambda: ymm_update_frame(self))
        self.frame_timer.start(self.frame_timer_interval)
        
        self.follow_timer = QTimer()
        self.follow_timer.timeout.connect(lambda: self.update_position())
        self.follow_timer.start(self.follow_timer_interval)
        
        # ドラッグ用変数
        self._drag_pos = None
        
        # 右クリックメニューを有効化
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_context_menu)
        logger.info(f"YmmAvatarDialog.__init__ 完了")

    # Claude ウィンドウに追従
    def update_position(self):
        pvv_mcp_server.avatar.mod_update_position.update_position(self)
        return

    def save_config(self):
        """
        設定を辞書形式で返す
        
        Returns:
            dict: 設定辞書
        """
        self.frame_timer.stop()

        config = {
            "zip_path": self.zip_path,
            "app_title": self.app_title,
            "position": self.position,
            "flip": self.flip,
            "scale": self.scale_percent,
            "anime_types": self.anime_types,
            "frame_timer_interval": self.frame_timer_interval,
            "follow_timer_interval": self.follow_timer_interval,
            "dialogs" : {}
        }

        for animetype, dialog in self.ymm_dialogs.items():
            conf = dialog.save_config()
            config["dialogs"][animetype] = conf
        
        logger.info(f"save_config [YmmAvatarWindow]: {config}")
        
        self.frame_timer.start(self.frame_timer_interval)

        return config


    def load_config(self, config):
        """
        設定辞書から設定を読み込む
        
        Args:
            config: save_config()で保存した辞書
        """
        logger.info(f"load_config [YmmAvatarWindow]")
        
        self.frame_timer.stop()

        if "zip_path" in config:
            self.zip_path = config["zip_path"]
            logger.info(f"  zip_path: {config['zip_path']}")

        if "app_title" in config:
            self.app_title = config["app_title"]
            logger.info(f"  app_title: {config['app_title']}")

        if "position" in config:
            self.set_position(config["position"])
            logger.info(f"  position: {config['position']}")

        if "flip" in config:
            self.set_flip(config["flip"])
            logger.info(f"  flip: {config['flip']}")

        if "scale" in config:
            self.set_scale(config["scale"])
            logger.info(f"  scale: {config['scale']}")
        
        if "anime_types" in config:
            self.app_title = config["anime_types"]
            logger.info(f"  anime_types: {config['anime_types']}")
        
        if "frame_timer_interval" in config:
            self.set_frame_timer_interval(config["frame_timer_interval"])
            logger.info(f"  frame_timer_interval: {config['frame_timer_interval']}")
        
        if "follow_timer_interval" in config:
            self.app_title = config["follow_timer_interval"]
            logger.info(f"  follow_timer_interval: {config['follow_timer_interval']}")
        

        # 各パーツの設定を読み込み
        if "dialogs" in config:
            for anitype, dialog_config in config["dialogs"].items():
                if anitype in self.ymm_dialogs:
                    logger.info(f"  loading dialog: {anitype}")
                    self.ymm_dialogs[anitype].load_config(dialog_config)
                else:
                    logger.warning(f"  unknown dialog: {anitype}")

        self.frame_timer.start(self.frame_timer_interval)


    @Slot()
    def showWindow(self):
        """スレッドセーフなshow"""
        self.show()
    
    def right_click_context_menu(self, position: QPoint) -> None:
        """右クリックメニュー"""
        ymm_right_click_context_menu(self, position)
        return
    
    def mousePressEvent(self, event):
        """マウス押下イベント"""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.follow_timer.stop()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """マウス移動イベント(ドラッグ)"""
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """マウスボタン離したらドラッグ終了"""
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            event.accept()
    
    # セッター
    @Slot(str)
    def set_anime_key(self, anime_key):
        """アニメーションタイプを設定"""
        if anime_key in self.anime_types:
            self.anime_key = anime_key
            self.ymm_dialogs[anime_key].start_oneshot()

    
    def set_frame_timer_interval(self, val):
        """フレーム更新間隔を設定"""
        self.frame_timer_interval = val
        self.frame_timer.setInterval(self.frame_timer_interval)
        for animetype, dialog in self.ymm_dialogs.items():
          dialog.set_frame_timer_interval(self.frame_timer_interval)
    
    def set_position(self, val):
        """表示位置を設定"""
        self.position = val
    
    def set_flip(self, val):
        """左右反転を設定"""
        self.flip = val
        for animetype, dialog in self.ymm_dialogs.items():
          dialog.set_flip(self.flip)

    def set_scale(self, val):
        """スケール設定"""
        self.scale = val
        for animetype, dialog in self.ymm_dialogs.items():
          dialog.set_scale(self.scale)

if __name__ == "__main__":
    
    zip_file = "C:\\work\\lambda-tuber\\ai-trial\\mission16\\docs\\ゆっくり霊夢改.zip"
    #zip_file = "C:\\work\\lambda-tuber\\ai-trial\\mission16\\docs\\れいむ.zip"
    #zip_file = "C:\\work\\lambda-tuber\\ai-trial\\mission16\\docs\\josei_20_pw.zip"

    app = QApplication(sys.argv)
    
    # YMMアバターウィンドウを作成
    # 実際のZIPファイルパスを指定してください
    avatar = YmmAvatarWindow(
        zip_path=zip_file,
        app_title="Claude",
        anime_types=["立ち絵", "口パク"],
        flip=False,
        scale_percent=50,
        position="right_out"
    )
    
    avatar.show()
    conf = avatar.save_config()    
    print(conf)

    conf["dialogs"]["立ち絵"]["parts"]["顔"]["base_image"] = "06b.png"
    avatar2 = YmmAvatarWindow(
        zip_path=zip_file,
        app_title="Claude",
        anime_types=["立ち絵", "口パク"],
        flip=False,
        scale_percent=50,
        position="right_out",
        config=conf)
    
    avatar2.show()

    sys.exit(app.exec())