from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QListWidget, QListWidgetItem,
    QVBoxLayout, QHBoxLayout, QScrollArea
)
from PySide6.QtWidgets import QHBoxLayout, QLabel, QRadioButton, QButtonGroup
from PySide6.QtCore import Qt
import sys
import random
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


class AvatarPartWidget(QWidget):
    def __init__(self, part_name, image_files):
        super().__init__()
        self.part_name = part_name
        self.image_files = image_files
        if len(self.image_files) > 0:
          self.base_image = image_files[0]
        else:
          self.base_image = None

        self.current_image = self.base_image
        self.selected_files = []
        self.update_idx = 0    
        self.interval = 3     # 全体側が100msec、このパーツは、300msecで更新する。
        self.anime_type = "固定"
                          # 固定 : base画像固定
                          # ループ : アニメ画像ループ
                          # ランダムA : base画像(ランダムtick) + アニメ画像(oneshot) 
                          # ランダムB : 立ち絵として、選択画像をランダムに表示する。 
        self.random_wait_tick = random.choice([10, 20, 30, 40, 50])
        self.random_wait_idx = 0
        self.random_anime_idx = 0
        self.loop_anime_idx = 0

        self._setup_gui()


    def update(self):

        if len(self.image_files) == 0:
            return None

        if self.update_idx < self.interval:
            self.update_idx = self.update_idx + 1
            return self.current_image

        self.update_idx = 0

        if self.anime_type == "固定":
            self.current_image = self.base_image

        if self.anime_type == "ループ":
            self._update_loop()

        if self.anime_type == "ランダムA":
            self._update_random_a()

        if self.anime_type == "ランダムB":
            self._update_random_b()

        return self.current_image

    def _update_loop(self):
        self.current_image = self.selected_files[self.loop_anime_idx]
        self.loop_anime_idx = (self.loop_anime_idx + 1) % len(self.selected_files)

    def _update_random_a(self):
        """ランダムA: base画像をランダム時間表示 → アニメ画像をワンショット再生"""
        
        # アニメ再生中かどうかのフラグチェック
        # random_anime_idx が 0 なら待機中、0より大きければアニメ再生中
        
        if self.random_anime_idx == 0:
            # 待機モード: base画像を表示
            self.current_image = self.base_image
            
            # カウントアップ
            self.random_wait_idx += 1
            
            # ランダム待機時間に達したらアニメ開始
            if self.random_wait_idx >= self.random_wait_tick:
                self.random_wait_idx = 0
                # 次のランダム待機時間を設定
                self.random_wait_tick = random.choice([10, 20, 30, 40, 50])
                logger.info(f"random_wait_tick : { self.random_wait_tick}")

                # アニメ画像が選択されていればアニメ開始
                if len(self.selected_files) > 0:
                    self.random_anime_idx = 1  # アニメ開始フラグ
        
        else:
            # アニメ再生モード
            # インデックスは1始まりなので、実際の配列アクセスは -1
            idx = self.random_anime_idx - 1
            
            if idx < len(self.selected_files):
                self.current_image = self.selected_files[idx]
                self.random_anime_idx += 1
            else:
                # アニメ終了: 待機モードに戻る
                self.random_anime_idx = 0
                self.current_image = self.base_image
                
    def _update_random_b(self):
        """ランダムB: selected_filesからランダムに1つ選んで、ランダムな時間表示"""
        
        # カウンタをインクリメント
        self.random_wait_idx += 1
        
        # まだ待機時間に達していない場合は、現在の画像をそのまま返す
        if self.random_wait_idx < self.random_wait_tick:
            return
        
        # 待機時間に達したら、次の画像に切り替え
        self.random_wait_idx = 0
        
        # 次のランダムな待機時間を設定(50~300tick)
        self.random_wait_tick = random.choice([10, 20, 30, 40, 50])
        logger.info(f"random_wait_tick : { self.random_wait_tick}")

        # ランダムに画像を選択
        if len(self.selected_files) > 0:
            self.current_image = random.choice(self.selected_files)
        else:
            # フォールバック
            self.current_image = self.base_image


    def _setup_gui(self):
        main_layout = QVBoxLayout(self)

        # 1段目: パーツ名
        part_name_layout = QHBoxLayout()
        part_name_layout.addWidget(QLabel("パーツ名:"))  # 左列
        part_name_layout.addWidget(QLabel(self.part_name))       # 右列（パーツ）
        part_name_layout.addStretch(1)
        main_layout.addLayout(part_name_layout)

        # 2段目: ベース画像
        base_layout = QHBoxLayout()
        base_layout.addWidget(QLabel("ベース画像:"))    # 左列
        self.combo_base = QComboBox()
        self.combo_base.addItems(self.image_files)
        self.combo_base.currentTextChanged.connect(self._update_base_image)
        base_layout.addWidget(self.combo_base)             # 右列
        base_layout.addStretch(1)
        main_layout.addLayout(base_layout)

        # 3段目: アニメ画像
        anim_layout = QHBoxLayout()
        anim_layout.addWidget(QLabel("アニメ画像:"), alignment=Qt.AlignTop)    # 左列
        self.list_anim = QListWidget()
        self.list_anim.setSelectionMode(QListWidget.MultiSelection)
        for f in self.image_files:
            self.list_anim.addItem(QListWidgetItem(f))
        self.list_anim.itemSelectionChanged.connect(self._update_selected_files)
        self.list_anim.setMaximumHeight(100)
        #rows = len(self.image_files)  # 表示したい行数
        #self.list_anim.setFixedHeight(self.list_anim.sizeHintForRow(0) * rows + 2 * self.list_anim.frameWidth())

        anim_layout.addWidget(self.list_anim)             # 右列
        main_layout.addLayout(anim_layout)

        # 4段目: interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("インターバル:"))    # 左列
        self.combo_interval = QComboBox()
        self.combo_interval.addItems(["1", "2", "3", "4", "5"])
        self.combo_interval.setCurrentIndex(2)
        self.combo_interval.currentTextChanged.connect(self._update_interval)
        interval_layout.addWidget(self.combo_interval)             # 右列
        interval_layout.addStretch(1)
        main_layout.addLayout(interval_layout)

        # 5段目: アニメーションタイプ
        anim_type_layout = QHBoxLayout()
        anim_type_layout.addWidget(QLabel("アニメタイプ:"))  # 左列ラベル

        # ラジオボタンを作成
        self.radio_fixed = QRadioButton("固定")
        self.radio_loop = QRadioButton("ループ")
        self.radio_random_a = QRadioButton("ランダムA")
        self.radio_random_b = QRadioButton("ランダムB")

        # ボタングループにまとめて排他選択を有効化
        self.anim_type_group = QButtonGroup(self)
        self.anim_type_group.addButton(self.radio_fixed)
        self.anim_type_group.addButton(self.radio_loop)
        self.anim_type_group.addButton(self.radio_random_a)
        self.anim_type_group.addButton(self.radio_random_b)
        self.anim_type_group.buttonClicked.connect(self._on_anim_type_changed)

        # 初期状態を設定（例: 固定をデフォルト選択）
        self.radio_fixed.setChecked(True)

        # レイアウトに追加（左寄せ）
        anim_type_layout.addWidget(self.radio_fixed)
        anim_type_layout.addWidget(self.radio_loop)
        anim_type_layout.addWidget(self.radio_random_a)
        anim_type_layout.addWidget(self.radio_random_b)
        anim_type_layout.addStretch(1)

        # メインレイアウトに追加
        main_layout.addLayout(anim_type_layout)


    def _update_selected_files(self):
        self.selected_files = [item.text() for item in self.list_anim.selectedItems()]
        print(f"selected_files: {self.selected_files}")

    def _update_base_image(self, text):
        self.base_image = text
        print(f"base_image: {self.base_image}")

    def _update_interval(self, text):
        self.interval = int(text)
        print(f"interval: {self.interval}")

    def _on_anim_type_changed(self, button):
        self.anime_type = button.text()
        print(f"選択されたアニメーションタイプ: {self.anime_type}")

        # 共通のカウンタをリセット
        self.update_idx = 0
        
        # ループ用カウンタをリセット
        self.loop_anime_idx = 0
        
        # ランダムA用カウンタをリセット
        self.random_anime_idx = 0
        self.random_wait_idx = 0
        self.random_wait_tick = random.choice([10, 20, 30, 40, 50])
        logger.info(f"random_wait_tick : { self.random_wait_tick}")        

        # ランダムB用カウンタをリセット
        # (random_wait_idx, random_wait_tickは共用なので上で初期化済み)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # サンプルパーツ
    part_widget = AvatarPartWidget("目", ["01.png", "02.png", "03.png", "04.png", "05.png", "06.png", "07.png"])
    part_widget.show()

    sys.exit(app.exec())

