# DBサーバ仕様書

## Network
- IP: 172.16.0.174
- Host名: db

## セキュリティ
- firewalld: OFF
- selinux: OFF

## User
- root

## パッケージ
| 名称    | 種別     | バージョン |
|---------|---------|---------|
| wget    | dnf     | 最新     |
| apache  | dnf     | 最新     |

## Service
| 名称    | 状態     |
|---------|---------|
| cockpit    | disable |
| firewalld  | disable |
| apache     | enable |

# DBサービス
- ミドルウエア : postgresql
- ポート : 5432
- schema : public
    - table : tel
      - column : name(string), number(string)

