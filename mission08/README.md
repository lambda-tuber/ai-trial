# Tachikoma Agents

## コンセプト
本プロジェクトでは、**LLM + MCP で成り立つ AI Agent** を攻殻機動隊に登場する「タチコマ」として定義します。
- **LLM**：思考・推論を担う頭脳
- **MCP**：環境との接続を担う多脚戦車のような外殻  

攻殻機動隊におけるタチコマは、人工衛星上の AI を頭脳とし、  
現実世界に存在する多脚戦車として行動します。  

同様に本実装では：

- **LLM**: [LM Studio](https://lmstudio.ai/) などを利用したローカル LLM  
- **MCP**: `stdio` モードで動作する [pty-mcp-server](https://github.com/modelcontextprotocol) などを利用  

を組み合わせることで、「タチコマ」と呼ぶ自律型エージェントを構築します。  

---

## 構成要素
- **LLM (Local Large Language Model)**  
  - LM Studio を用いてローカル推論を実行  
  - モデルは `gpt-oss-20b` などを指定可能  

- **MCP (Model Context Protocol) サーバ**  
  - `pty-mcp-server` を利用して、標準入出力 (stdio) で接続  
  - 外部環境との I/O を担当  

- **Agent (Tachikoma)**  
  - LLM を頭脳とし、MCP サーバを通じてタスクを実行  
  - 複数のタチコマが存在し、相互にツール経由でメッセージを送受信可能  

---
## 実装例 MAGIシステム

エヴァンゲリオンに登場する「MAGI システム」は、  
人類補完計画や NERV の意思決定を担う **三重人格型スーパーコンピュータ** です。  

- **MELCHIOR（メルキオール）** : 学者（科学者）としての人格  
- **BALTHASAR（バルタザール）** : 母親としての人格  
- **CASPER（カスパー）** : 女性としての人格  

これら三者が多数決で最終意思決定を行う仕組みであり、  
本実装では調停役として、**葛城ミサト（指揮官的役割）** エージェントも追加しています。

以下は、タチコマ（エージェント）の一例です。  
この例では、**LM Studio に接続された LLM** と、**MCP サーバ**の指定によって、  
「ミサト」というタチコマが構成されます。  

```python
tachikoma_list = [
    {
        "name": "misato",                                      # 注：1件目がエントリープラグ(starting_agent)になる。
        "description": "MAGIシステムの三賢者を束ねるミサト",
        "llm": {                                               # LLM による頭脳
            "model": "gpt-oss-20b",
            "base_url": "http://172.16.0.43:1234/v1",
            "api_key": "lmstudio"
        },
        "mcp_servers": [],                                     # デフォルトMCPサーバに追加があれば記載する。
        "prompts": [],                                         # デフォルトプロンプトに追加があれば記載する
        "resources": ["file:///MAGI_system_definition.md"],    # デフォルトリソースに追加があれば記載する
    }
]
```

## Setup
1. git cloneする。
2. python環境を準備する。
3. pty-mcp-serverをインストールする。
4. magi_system.pyのtachikoma_listを適宜編集する。
5. magi_system.pyを実行する。

## 利用ツール一覧
- [Microsoft Clipchamp](https://apps.microsoft.com/detail/9p1j8s7ccwwt?hl=ja-JP&gl=JP)
- [AivisSpeech](https://aivis-project.com/)

## Youtubeショート一覧
### xxxxxx

[![No.1](https://img.youtube.com/vi/xxxxxxxx/maxresdefault.jpg)](https://youtube.com/shorts/xxxxxx)

