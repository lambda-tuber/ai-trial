
# 機能仕様
画像を表示する透明なWindowsを提供する。
- 表示位置指定機能 : 左クリックのドラッグで移動できる。
- 表示位置追随機能 : ターゲットアプリ(Claude)のWindowsを移動した場合に、追随する。
- アニメーション機能 : 立ち絵や、口パクなど、PNG画像を差し替えてアニメーションする。
- 左クリックドラッグ機能 : Avatarウィンドウを移動できる。
- 右クリックメニュー
  - アニメーション指定機能 : 立ち絵や、口パクなど、表示するアニメーションを指定できる。
  - 表示位置追随設定 : 表示位置隋髄機能のオン／オフを設定する。
  - アニメーション速度設定 : PNGの差し替え間隔を指定する。

---

# 詳細設計
## 方針
- 統合クラス、self渡し関数方式で、モジュール分割を行う実装。

## package
- 名前 : pvv_mcp_server
- pkg_dir : <prj_dir>\pvv_mcp_server

## 依存パッケージ
- PySide6
- pygetwindow
- opencv-python

## mod_avatarモジュール
- 概要 : 統合クラス。
- ファイル : <pkg_dir>\avatar\mod_avatar.py 
- クラス : AvatarWindow(QWidget)
- 関数
  -__init__ : コンストラクタ

## mod_load_pixmapsモジュール
- 概要 : anime_keyごとの画像ファイルを読み込んで、QPixmapの連想配列を返す。
- ファイル : <pkg_dir>\avatar\mod_load_pixmaps.py 
- UnitTest : <prj_dir>\tests\avatar\test_load_pixmaps.py 
- 関数 : load_pixmaps
  - 概要 : アニメーション画像を事前に読み込んでおく。
  - 引数
    1. self : AvatarWindowのインスタンス
    2. image_dict : anime_keyとアニメーション画像リストの連想配列。
    3. scale_percent : 画像の縮尺変更パーセント値
    4. flip : 画像を左右反転するかのbool値

## mod_update_frameモジュール
- 概要 : self.label(QLabel)の画像を差し替える。
- ファイル : <pkg_dir>\avatar\mod_update_frame.py 
- UnitTest : <prj_dir>\tests\avatar\test_update_frame.py 
- 関数 : update_frame
  - 概要 : self.label(QLabel)の画像を差し替える。
  - 引数
    1. self : AvatarWindowのインスタンス
  - 処理
    1. self.pixmap_dictから、self.anime_keyに該当する画像リストを取得する。
    2. 画像リストのself.anime_indexを取得し、self.label.setPixmapに設定する。
    3. self.anime_indexをインクリメントする。ただし、画像リスト長を超える場合は、0を設定する。

## mod_update_positionモジュール
- 概要 : self.app_titleで指定されたアプリケーションウィンドウの左下外側(left_out)、左下内側(left_in)、右下内側(right_in)、右下外外側(right_in)に下揃えするように、self(AvatarWindow)を移動する。
- ファイル : <pkg_dir>\avatar\mod_update_position.py 
- UnitTest : <prj_dir>\tests\avatar\test_update_position.py 
- 関数 : update_position
  - 概要 :self.app_titleで指定されたアプリケーションウィンドウの左下外側(left_out)、左下内側(left_in)、右下内側(right_in)、右下外外側(right_in)に下揃えするように、self(AvatarWindow)を移動する。
  - 引数
    1. self : AvatarWindowのインスタンス
  - 処理
    1. self.app_titleで指定されたアプリケーションウィンドウを特定する。
    2. アプリケーションウィンドウの位置(x,y)、幅、高さを特定する。
    3. self.positionで指定された表示位置に従い、selfの移動先を算出し、移動を実行する。

## mod_right_click_context_menuモジュール
- 概要 : アバターを右クリックした際に表示するメニューを定義する。
- ファイル : <pkg_dir>\avatar\mod_right_click_context_menu.py 
- UnitTest : <prj_dir>\tests\avatar\test_right_click_context_menu.py 
- 関数 : update_position
  - 概要 :アバターを右クリックした際に表示するメニューを定義する。
  - 引数
    1. self : AvatarWindowのインスタンス
    2. postion : クリック位置
  - 処理
    1. アニメーション選択サブメニューの定義
    2. アニメーション速度設定サブメニューの定義
    3. 表示位置選択サブメニューの定義
    4. 左右反転メニューの定義
    5. 位置追随設定の定義

