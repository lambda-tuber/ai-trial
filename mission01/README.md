# Claudeで家計簿(みたいなの)をつけてみた

ClaudeやChatGPT、その他、LM Studio、OllamaといったAI関連アプリ、ツールを使って、どんなことができるのか、いろいろお試し中です。
うまくうごいたら、紹介していきます。

関連資料は、以下を参照願います。
https://github.com/lambda-tuber/ai-trial

この連載では、AIに簿記の記録をさせる実験として **家計簿作成** を試してみました。  
AIには MCP ツールとして以下の機能を提供しています：

1. **仕訳インターフェース**  
   - 借方・貸方勘定科目や金額を指定して、仕訳ファイルを自動生成。  
   - 備考や日時はオプションで指定可能。省略すると現在日時が自動使用されます。  
   - 仕訳データは **階層ディレクトリ＋タイムスタンプ＋UUID** で整理され、CSVログにも追記。プロセス再起動後もデータは保持されます。

2. **勘定サマリー取得**  
   - 指定した勘定科目・年月の仕訳ファイルをスキャンして、借方・貸方の合計を計算。  
   - 差引残高（Balance）を算出し、借方／貸方どちらに残高があるかも判定。  
   - 借方・貸方の金額は、仕訳ファイルのサイズ（バイト数）で保持され、集計可能。

AIはこれらのツールと保存方式を組み合わせて、家計簿データの作成と集計を自律的に実行しています。  

⚠️ **注記**：これはあくまで実験的な取り組みであり、実際の会計処理や税務処理には使用できません。


## Setup
1. Claudeの[ファイル]→[設定]→[拡張機能]を開きます。
2. MCPサーバである[pty-mcp-server](https://github.com/phoityne/pty-mcp-server)を[dxtインストール](https://github.com/phoityne/pms-dxt)します。 
3. Claudeの[ファイル]→[設定]→[拡張機能]から[詳細設定]を開きます。
4. [拡張機能フォルダを開く]を選択し、pty-mcp-serverの[設定ファイル](https://github.com/phoityne/pms-missions/blob/main/0001_default-assets/pty-mcp-server.yaml)で、prompts, resources, toolsフォルダを指定します。

## 利用ツール一覧
- [Claude(Descktop)](https://claude.ai/download)
- [pty-mcp-server](https://github.com/phoityne/pty-mcp-server)
- [Microsoft Clipchamp](https://apps.microsoft.com/detail/9p1j8s7ccwwt?hl=ja-JP&gl=JP)
- [AivisSpeech](https://aivis-project.com/)

## Youtubeショート一覧
### No.1 [AI] Claudeで家計簿(みたいなの)をつけてみた

[![No.1](https://img.youtube.com/vi/1Gb_H-ES_bY/maxresdefault.jpg)](https://youtube.com/shorts/1Gb_H-ES_bY)

### No.2 [AI] Claudeで家計簿(みたいなの)をつけてみた 改良版

[![No.2](https://img.youtube.com/vi/wKDSnlEK1YU/maxresdefault.jpg)](https://youtube.com/shorts/wKDSnlEK1YU)

### No.3 [AI] Claudeで家計簿(みたいなの)をつけてみた まとめて仕訳

[![No.3](https://img.youtube.com/vi/zBnCXTHS7Ms/maxresdefault.jpg)](https://youtube.com/shorts/zBnCXTHS7Ms)

### No.4 [AI] Claudeで家計簿(みたいなの)をつけてみた 現金あるかな

[![No.4](https://img.youtube.com/vi/0_KedOvhN7I/maxresdefault.jpg)](https://youtube.com/shorts/0_KedOvhN7I)

### No.5 [AI] Claudeで家計簿(みたいなの)をつけてみた P/Lをつくってもらう

[![No.5](https://img.youtube.com/vi/cdI5DQN_nS8/maxresdefault.jpg)](https://youtube.com/shorts/cdI5DQN_nS8)

