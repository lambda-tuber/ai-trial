# DBサーバ仕様書

## 基本情報
- OS: Almalinux 10
- User
    - root

## Network
- IP1: 172.16.0.174
- IP2: 192.168.0.174
- ホスト名: db

## セキュリティ
- firewalld: OFF
- selinux: OFF


## パッケージ
| 名称    | 種別     | バージョン |
|---------|---------|---------|
| wget    | dnf     | 最新     |
| postgresql-server  | dnf     | 最新     |


## Service
| 名称    | 状態     |
|---------|---------|
| cockpit    | static |
| firewalld  | disable |
| postgresql     | enable |


## DBサービス
- ミドルウエア : postgresql
- ポート : 5432
- データベースクラスタ : /var/lib/pgsql/data
- アクセス制限
   - ローカルUNIXソケット : すべてのユーザを trust で許可    (local   all   all   trust)
   - IPv4 すべてのアドレスから すべてのユーザを trust で許可  (host    all   all 0.0.0.0/0 trust)
- schema : public
   - database : iaai
      - table : tel
        - column : name(string), number(string)
        - データ数 : 2件
            - hoge, 0120-1234-5678
            - fuga, 080-9876-5432
