# DBサーバ仕様書

## OS
- name: Almalinux 10

## Network
- IP: 172.16.0.174
- ホスト名: db

## セキュリティ
- firewalld: OFF
- selinux: OFF

## User
- root

## パッケージ
| 名称    | 種別     | バージョン |
|---------|---------|---------|
| wget    | dnf     | 最新     |
| postgresql  | dnf     | 最新     |

## Service
| 名称    | 状態     |
|---------|---------|
| cockpit    | disable |
| firewalld  | disable |
| postgresql     | enable |

# DBサービス
- ミドルウエア : postgresql
- ポート : 5432
- schema : public
    - table : tel
      - column : name(string), number(string)

