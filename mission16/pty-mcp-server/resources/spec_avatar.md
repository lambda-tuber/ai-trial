
# 機能仕様
画像を表示する透明なWindowsを提供する。
- 表示位置指定機能 : 
- 表示位置追随機能 : 
- アニメーション機能 : 
- 左クリックドラッグ機能 : 
- 右クリックメニュー
  - アニメーション指定機能 : 
  - 表示位置追随設定 : 
  - アニメーション速度設定 : 

---

# 詳細設計
## 方針
- 統合クラス、self渡し関数方式で、モジュール分割を行う実装。

## package
- 名前 : pvv_mcp_server
- pkg_dir : <prj_dir>/pvv_mcp_server

## 依存パッケージ
- mcp
- requests
- sounddevice
- numpy

## mod_avatarモジュール
- 概要 : 統合クラス。
- ファイル : <pkg_dir>/mod_avatar.py 
- 関数
  - _init_ : コンストラクタ


