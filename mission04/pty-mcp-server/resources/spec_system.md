# Network

* IP: 172.16.0.172
* Host名: www

# User

* root

# セキュリティ
- selinux: オン
- firewalld: オン

# パッケージ

| 名称    | 種別     | バージョン |
|---------|---------|---------|
| wget    | dnf     | 最新     |
| apache  | dnf     | 最新     |

# Service

| 名称    | 状態     |
|---------|---------|
| cockpit    | disable |
| firewalld  | disable |
| apache     | enable |

