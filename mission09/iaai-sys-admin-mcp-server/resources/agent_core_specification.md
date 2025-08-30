# IaAI システム仕様書

## 言語
- 日本語

## ネットワーク構成
- セグメント: 172.16.0.0/16

## システム構成
- 仮想サーバ: 3台
  - WWWサーバ
  - APサーバ
  - DBサーバ

## 管理者アカウント
- root

## 機能
- 公開Webサイトにおいて、IaAIに関する情報を発信する。


## AIシステム構成
- IaAI システム管理者
  - IP: 172.16.0.198
  - ホスト名:k-pc
  - GPU: GeForce RTX 4060
  - サービス: LM Studio
  - モデル: gpt-oss-20b
- WWWサーバ管理者 (www-sv-admin)
  - IP: 172.16.0.43
  - ホスト名:n-note
  - GPU: GeForce RTX 4050 Laptop
  - サービス: LM Studio
  - モデル: phi-4-reasoning-plus
- APサーバ管理者 (ap-sv-admin)
  - IP: 172.16.0.99
  - ホスト名:t-pc
  - GPU: GeForce RTX 3060
  - サービス: LM Studio
  - モデル: gemma-3-12b
- DBサーバ管理者 (db-sv-admin)
  - IP: 172.16.0.100
  - ホスト名:o-note
  - GPU: GeForce RTX 3050 Laptop
  - サービス: LM Studio
  - モデル: phi-4-mini-reasoning

