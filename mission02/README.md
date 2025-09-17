# ClaudeのIaC
本連載では、Claude を活用し、次世代のシステム開発スタイルを探究しています。  
MCPを付与されたAIは、SSH・Telnet・Serial通信など多様な手段でリモート接続し、現実のシステムへ直接アクセスすることが可能になります。

これは、AIに「実行環境へ作用する手」を与えることに相当し、従来の対話型アシスタントを越えて、より実務的な役割を担わせるものです。  
この仕組みによって、AI自身が IaC（Infrastructure as Code） の実践主体となり、設定変更や運用タスクを自律的に遂行できる可能性が広がります。

この強力な能力を安全かつ制御可能に扱うため、MCPは3つの主要な機能を提供します：
- Resources（仕様書）  
システムのwhy（目的）やwhat（内容）を定義した情報を提供。  
ここでいうIaCのスペック（構築対象の仕様）が明文化されます。
- Prompts（指示・手順）  
AIの役割、振る舞い、手順、制御、制約、指示を明確化。  
AIがシステム管理者としてどう振る舞うかを形成します。
- Tools（実行手段）  
SSHやTelnetなど、実際に環境に作用するための手段を提供。  
AIはこれを用いてResourcesとPromptsに基づいた操作を実現します。

この3要素により、AIはスペック指向でIaCを実行可能になります。
すなわち、Resourcesで定義された仕様に沿い、Promptsで役割や制御を定め、Toolsを介して実際にシステムを操作する、という一連の流れです。

⚠️ 注記：本取り組みはあくまでも実験的な検証です。AIにシステムへ直接アクセスさせることは強力である一方、常に危険性やリスクを伴うため、十分な制御と監視が不可欠です。

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
### No.1 [AI] ClaudeのIaC SSHしてみる

[![No.1](https://img.youtube.com/vi/EsHkvVj5Uis/maxresdefault.jpg)](https://youtube.com/shorts/EsHkvVj5Uis)

### No.2 [AI] ClaudeのIaC Claudeの挨拶

[![No.2](https://img.youtube.com/vi/3RhB2aQ5IWU/maxresdefault.jpg)](https://youtube.com/shorts/3RhB2aQ5IWU)

### No.3 [AI] ClaudeのIaC めざせSpec指向

[![No.2](https://img.youtube.com/vi/xCNnAn0wulQ/maxresdefault.jpg)](https://youtube.com/shorts/xCNnAn0wulQ)

### No.4 [AI] ClaudeのIaC Spec指向でホスト名設定

[![No.2](https://img.youtube.com/vi/oMKwLlMNCVY/maxresdefault.jpg)](https://youtube.com/shorts/oMKwLlMNCVY)

### No.5 [AI] ClaudeのIaC ツール調査

[![No.2](https://img.youtube.com/vi/SCOiEWDY2NA/maxresdefault.jpg)](https://youtube.com/shorts/SCOiEWDY2NA)

### No.6 [AI] ClaudeのIaC サービス調査

[![No.2](https://img.youtube.com/vi/zVjOlWi9m0E/maxresdefault.jpg)](https://youtube.com/shorts/zVjOlWi9m0E)

### No.7 [AI] ClaudeのIaC システム現状確認

[![No.2](https://img.youtube.com/vi/qhthdNqFbDI/maxresdefault.jpg)](https://youtube.com/shorts/qhthdNqFbDI)
