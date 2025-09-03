# WWWサーバ仕様書

## 基本情報
- OS: Almalinux 10
- User
    - root

## Network
- eth0: 172.16.0.172
- eth1: 192.168.0.172
- Host名: www

## セキュリティ
- firewalld: OFF
- selinux: OFF

## パッケージ
| 名称    | 種別     | バージョン |
|---------|---------|---------|
| wget    | dnf     | 最新     |
| httpd  | dnf     | 最新     |

## Service
| 名称    | 状態     |
|---------|---------|
| cockpit    | static |
| firewalld  | disable |
| httpd     | enable |

# Webサービス
- ミドルウエア : apache httpd
- ポート : 80
- proxy
    - uri : "/tel"
    - 転送プロトコル : ajp
    - 転送先IP : 172.16.0.173 (APサーバ)
    - 転送先URI : /tel
    - 転送先ポート : 8009
