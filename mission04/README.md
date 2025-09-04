# mission04

CloudeやChatGPT、その他、LM Studio、OllamaといったAI関連アプリ、ツールを使って、どんなことができるのか、いろいろお試し中です。

うまくうごいたら、紹介していきます。


ローカルLLM
- continue + ollama
- python + lm studio
- python agent
- multi agent


```
harmony

TEMPLATE """{{- if .System -}}<|start|>system<|message|>{{ .System }}<|end|>
{{- end -}}{{- range .Messages -}}<|start|>{{ .Role }}<|message|>{{ .Content }}<|end|>
{{- end -}}<|start|>assistant<|message|>"""
PARAMETER stop "<|end|>"
```