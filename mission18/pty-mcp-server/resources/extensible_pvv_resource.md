# Extensible Resource：pvv-mcp-server Knowledge Base

## 概要

このリソースは、pvv-mcp-server（略称：ぷぶ）の開発に関する
個別的・具体的な知識とデータを記録する。

これは「拡張」の方向性であり、core には含まれない。

---

## プロジェクト情報

### プロジェクト構成

**メインフォルダ：**
ぶらぶらぶら

**MCP サーバー構成：**
ぶらぶらぶら

---

## Voicevox キャラクター仕様

### 利用可能なキャラクター

1. **四国めたん（惣流・アスカ・ラングレー役）**
   - style_id: 6
   - ツール: speak_metan_aska, emotion_metan_aska
   - 特徴: ツンデレ、元気、挑発的

2. **黒乃ネコ（ユーザー役）**
   - style_id: 11
   - ツール: speak_kurono_neko, emotion_kurono_neko
   - 特徴: ユーザーの発言を代弁

3. **つむぎ（博麗霊夢役）**
   - style_id: 要確認
   - ツール: speak_tumugi_reimu, emotion_tumugi_reimu
   - 特徴: 東方Project キャラクター

4. **ずんだもん（霧雨魔理沙役）**
   - style_id: 要確認
   - ツール: speak_zunda_marisa, emotion_zunda_marisa
   - 特徴: 東方Project キャラクター

### 音声合成パラメータ

**デフォルト値：**
- speedScale: 1.0（話速）
- pitchScale: 0.0（声の高さ）
- intonationScale: 1.0（抑揚）
- volumeScale: 1.0（音量）

---

## 開発履歴

### 実装済み機能

1. **音声チャット機能**
   - 日付: 2025年12月頃
   - 内容: Voicevox を使用した音声発話システム
   - 特徴: キャラクター別の音声、感情表現対応

2. **check-project-status ツール**
   - 日付: 2025年12月27日頃
   - 内容: プロジェクト全体の状況を一括確認
   - 特徴: フォルダ構造、リスト表示

3. **Core Candidate ファイル**
   - 日付: 2025年12月28日
   - 内容: 自己進化型 AI Agent の概念整理
   - 特徴: 拡張と適応の二軸理論

---

## 技術的な詳細

### MCP ツールの実装

**利用可能な MCP ツール：**
- proc-spawn: プロセス起動
- proc-terminate: プロセス終了
- proc-message: プロセスへのメッセージ送信
- proc-cmd: Windows コマンドプロンプト起動
- proc-ps: PowerShell 起動
- proc-ssh: SSH クライアント起動
- pms-list-dir: ディレクトリ一覧
- pms-read-file: ファイル読み込み
- pms-write-file: ファイル書き込み
- check-project-status: プロジェクト状況確認

### バッチファイルの文字コード

**重要な設定：**
ぶらぶらぶら

---

## 既知の問題と制約

### MCP 通知機能の未実装

**Issue 情報：**
- GitHub: anthropics/claude-code
- Issue 番号: 4118
- タイトル: Capture MCP Tools Changed notifications
- ステータス: Open（2025年7月22日時点）
- 担当: ollie-anthropic

**影響範囲：**
- tools/list_changed 通知が受け取れない
- prompts/list_changed 通知が受け取れない
- resources/list_changed 通知が受け取れない

**現状の対応：**
- 新しい要素追加後は手動で再起動が必要
- Claude セッションの再起動
- または MCP サーバーの再起動

---

## 開発環境

### 使用技術

**バックエンド：**
- MCP (Model Context Protocol)
- Voicevox（音声合成）
- Windows Batch スクリプト

**フロントエンド：**
- Claude.ai チャットインターフェース
- 音声出力
- アバター表示（Unity）

**開発ツール：**
- テキストエディタ
- コマンドプロンプト / PowerShell
- Git（バージョン管理）

---

## 関連プロジェクト

### AI Unity Avatar ツール

**概要：**
- Unity を使用した 3D アバター開発
- VRM、Live2D データ対応
- pvv-mcp-server との連携を想定

**状態：**
- 開発中
- 詳細は別ドキュメントに記載予定

### bokicast-mcp-server

**概要：**
- Qt を使用した簿記可視化ツール
- 仕訳、T字勘定、残高試算表の表示
- 教育・学習支援ツールとして開発

**状態：**
- 開発中
- 詳細は別ドキュメントに記載予定

---

## 参考リンク

### 外部ドキュメント

- MCP 仕様のサイト
- Voicevox のサイト
- Claude API のサイト

### 関連 Issue

- GitHub Issue 4118: MCP Tools Changed notifications

---

## メモと今後の課題

### 実装したい機能

- 音声パラメータの動的調整
- 複数キャラクター間の自然な対話
- ログ分析と可視化
- パフォーマンス測定とボトルネック特定
- Unity Avatar との連携強化

### 検討中の改善

- バッチツールの PowerShell 移行
- エラーハンドリングの強化
- ユニットテストの導入
- CI/CD パイプラインの構築

---

このリソースは、pvv-mcp-server の開発を通じて獲得した具体的な知識とデータである。
これは「拡張」であり、経験の蓄積として個別ファイルに保存される。
将来的には、より詳細なドキュメントや、他のプロジェクトの知識ベースと統合される可能性がある。
