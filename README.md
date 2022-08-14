# quaint-api
[![pytest](https://github.com/hibiya-itchief/quaint-api/actions/workflows/pytest.yml/badge.svg)](https://github.com/hibiya-itchief/quaint-api/actions/workflows/pytest.yml)
---
星陵祭オンライン整理券システム「QUAINT」のバックエンドAPI

## Dockerを使用した起動
### 依存関係
- docker https://docs.docker.com/get-docker/
- docker-compose
- git https://github.com/git-guides/install-git

をインストールしておく

### 手順
Gitリポジトリをクローン
```sh
$ git clone https://github.com/hibiya-itchief/quaint-api.git
```
dockerコンテナを立ち上げ
```sh
$ docker-compose up -d
```

http://127.0.0.1:8000/docs でAPIドキュメントが読める


## 開発するときに(僕が)よく使うコマンド(ただのメモ)
### FastAPI
uvicornサーバーの立ち上げ(変更を自動読み込み)
```sh
$ uvicorn main:app --reload
```
### migration
最新のapp/models/models.py のBaseクラスを読んでマイグレーションファイルを作る
```sh
$ alembic revision --autogenerate -m "hogehoge"
```
マイグレーションを実行 (+1,-1等で戻したり一個進めたりできるらしい)
```sh
$ alembic upgrade head
```
SchemaSpyでDBのER図を生成
```
sudo java -jar schemaspy.jar -t mysql -host localhost -db quaint-app -u quaint -p password -o ./db/schemaspy -dp db/driver/mysql-connector-java-8.0.29/mysql-connector-java-8.0.29.jar -s quaint-app -vizjs
```
### pip package
このディレクトリ以下で使ってるパッケージだけをrequirements.txtに記録
```sh
$ pipreqs . --force
```
