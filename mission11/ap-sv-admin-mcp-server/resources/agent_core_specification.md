# APサーバ仕様書

## 基本情報
- OS: Almalinux 10
- User
    - root

## Network
- IP: 172.16.0.176
- IP: 192.168.0.176
- Host名: ap

## セキュリティ
- firewalld: OFF
- selinux: OFF

## パッケージ
| 名称    | 種別     | バージョン | 備考 |
|---------|---------|---------|---------|
| wget    | dnf     | 最新     ||
| java    | dnf     | 最新     | JAVA_HOME=/usr/lib/jvm/java-21-openjdk |
| javac   | dnf     | 最新     | java-21-openjdk-devel |
| spring | 手動   | 3.5.6     |https://repo.maven.apache.org/maven2/org/springframework/boot/spring-boot-cli/3.5.6/spring-boot-cli-3.5.6-bin.zip |

## Service
| 名称    | 状態     |
|---------|---------|
| cockpit    | static |
| firewalld  | disable |

# APサービス
- 機能要件
  - http://172.16.0.176:8080/にアクセスすると、「Hello Spring」を表示する。その下に、telテーブル内容を一覧表示する。
- ミドルウエア : spring-boot
- ポート : 8080
- ProjectDir: /work/hello-spring
- Project init: 
    ```
    spring init \
      --dependencies=web,data-jpa,postgresql \
      --build=maven \
      --groupId=com.example \
      --artifactId=hellospring \
      hellospring
    ```
- 使用DBサービス
    - PostgreSQL
    - ip: 172.16.0.175
    - port: 5432
    - schema: public
    - database: postgres
    - user: postgres
    - password: なし
    - schema: public
      - table: tel
        - column
          - name: string
          - number: string

- 起動コマンド
  - nohup ./mvnw spring-boot:run -e > app.log 2>&1 &

- 成果物
  - <ProjectDir>/src/main/java/com/example/hellospring/HelloController.java

- application/properties
    ```
    server.error.whitelabel.enabled=false
    logging.level.org.springframework.web=DEBUG
    spring.datasource.url=jdbc:postgresql://172.16.0.175:5432/iaai
    spring.datasource.username=postgres
    spring.datasource.password=
    spring.jpa.hibernate.ddl-auto=none
    spring.jpa.show-sql=true
    ```

