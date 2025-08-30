# APサーバ仕様書

## Network
- IP: 172.16.0.173
- Host名: ap

## セキュリティ
- firewalld: OFF
- selinux: OFF

## User
- root

## パッケージ
| 名称    | 種別     | バージョン |
|---------|---------|---------|
| wget    | dnf     | 最新     |
| tomcat  | dnf     | 最新     |

## Service
| 名称    | 状態     |
|---------|---------|
| cockpit    | disable |
| firewalld  | disable |
| tomcat     | enable |

# Tomcatサービス
- ミドルウエア : tomcat
- ポート : 8080

# 機能
1. uri "/" にアクセスがあった場合、DBサーバのポート5432に接続する。
2. 以下のSQLをDBサーバにJDBCで発行する。
   ``` sql
   select name, number from tel; 
   ```
3. HTTP Responseとして、SQL結果をJSONデータで返す。
