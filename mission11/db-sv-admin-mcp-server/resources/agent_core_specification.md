# DBサーバ仕様書

## 基本情報
- OS: Almalinux 10
- User
    - root

## Network
- IP1: 172.16.0.175
- IP2: 192.168.0.175
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


## DBバックアップ仕様
- バックアップツール: pg_dumpall
- cron: 毎週日曜日 01:00に実行
- 実行ユーザ: root
- バッチファイル: /work/backup/bin/pg_backup.sh
- ログファイル: /work/backup/logs/pg_backup.log
- 保存場所: /work/backup/data
- 圧縮: 有
- 世代管理: 3世代 
- バックアップファイル名: pg_backup_yyyymmdd_世代数.gz

