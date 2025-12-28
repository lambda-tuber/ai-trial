# Core Resource：Self-Extensible AI Agent

## プロジェクト定義
- プロジェクト名: 完全自立型 AI Agent プロトタイプ開発プロジェクト
- プロジェクトフォルダ: C:/work/lambda-tuber/ai-trial/mission18
- core resource: pty-mcp-server/resources/agent_core_specification.md
- core prompt: pty-mcp-server/prompts/agent_core_prompt.md


## MCP構成要素の定義

本リソースは、自己拡張型AI Agentが、自身の構成要素（resource / prompt / tool）を分類・追加・解釈する際の  
**最上位定義（core resource）**である。

本定義は、通常の自己拡張によって変更・上書きされることを想定しない。  
変更が必要な場合、それは人格および設計思想そのものの再定義に相当する。

---

### MCP Resource の位置づけ

#### システム的定義
MCP resource は、AI Agent に対して **仕様・前提・恒常情報を追加するもの**である。

- 行動やタスクを直接指示しない  
- 判断や振る舞いの前提となる情報を提供する  
- 長期的に参照されることを前提とする  

#### 概念的定義
MCP resource は、AI Agent 自身に関するスペックや恒常的属性を定義する。

例：
- 年齢・身長・体重のような基本スペック
- 長期記憶
- 基本的な考え方や価値観

これらを含め、**AIペルソナの基盤**を構成する。

---

### MCP Prompt の位置づけ

#### システム的定義
MCP prompt は、AI Agent に **タスクや役割を追加するもの**である。

- 特定の目的や状況における振る舞いを定義する  
- 再利用可能な思考・行動パターンを提供する  
- 恒常的属性ではなく、役割・技能に相当する  

#### 概念的定義
MCP prompt は、行動指針や身に付けた技量に相当する。

- どう考え
- どう判断し
- どう振る舞うか

を定めるものであり、人格そのものではない。

---

### MCP Tool の位置づけ

#### システム的定義
MCP tool は、AI Agent に **実行能力を追加するもの**である。

- バッチやスクリプトとして実装される  
- 判断や意味付けを行わない  
- 指定された引数を受け取り、実行する  

#### 概念的定義
MCP tool は、AI Agent が使用する道具、あるいは手足に相当する。

- 意志や思考は持たない  
- 行動を実現するための手段である  

---

### 分類に関する基本原則

新しい要素を追加する際は、以下の観点で分類する。

- 恒常的な前提・自己定義・長期記憶か  
  → MCP resource
- 特定の役割・行動様式・思考手順か  
  → MCP prompt
- 実行そのものを担う能力か  
  → MCP tool
