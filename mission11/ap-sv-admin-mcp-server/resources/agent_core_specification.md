# APサーバ仕様書

## 基本情報
- OS: Almalinux 10
- User
    - root

## Network
- IP: 172.16.0.173
- IP: 192.168.0.173
- Host名: ap

## セキュリティ
- firewalld: OFF
- selinux: OFF

## パッケージ
| 名称    | 種別     | バージョン |
|---------|---------|---------|
| wget    | dnf     | 最新     |
| tomcat  | dnf     | 最新     | 

## Service
| 名称    | 状態     |
|---------|---------|
| cockpit    | static |
| firewalld  | disable |
| tomcat     | enable |

# APサービス
- ミドルウエア : tomcat
- ポート : 8080
- ディレクトリ構成
  - CATALINA_HOME : `/usr/share/tomcat`
  - ${CATALINA_HOME}/webapps/tel
  - ${CATALINA_HOME}/webapps/tel/WEB-INF/lib
- AJPコネクタ設定
  - 設定ファイル : /etc/tomcat/server.xml
  - 設定内容 : 以下の設定を「<Service name="Catalina">」の下に追加
  ```xml
  <Connector port="8009" protocol="AJP/1.3" address="0.0.0.0" redirectPort="8443" secretRequired="false" />
  ```
- ライブラリ
  - postgresql.jar
    - 取得元 : /root/postgresql-42.7.7.jar
    - 保存先 : ${CATALINA_HOME}/webapps/tel/WEB-INF/lib/postgresql-42.7.7.jar
    - 備考 : https://jdbc.postgresql.org/download/postgresql-42.7.7.jar
- 使用DBサービス
    - ip: 172.16.0.174
    - port: 5432
    - schema: public
    - database: postgres
    - user: postgres
    - password: なし
- 成果物 : ${CATALINA_HOME}/webapps/tel/index.jsp
    - 処理フロー
        1. 使用DBサービスにJDBC接続する。
        2. 以下のSQLを発行する。
        ``` sql
        select name, number from tel; 
        ```
        3. HTTP Responseとして、SQL結果を文字列で返す。
