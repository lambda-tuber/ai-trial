# WWWサーバ仕様書

## Network
- IP: 172.16.0.172
- Host名: www

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

# WWWサービス
- ミドルウエア : apache
- ポート : 80
- proxy
    - uri "/tomcat" を、APサーバの8080ポートに転送する。
