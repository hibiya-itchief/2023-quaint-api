# quaint-api
星陵祭オンライン整理券システム「QUAINT」のバックエンドAPI
## 目次
- [quaint-api](#quaint-api)
  - [目次](#目次)
  - [動かす](#動かす)
    - [必要条件](#必要条件)
    - [手順](#手順)
  - [ディレクトリ構成(ただのメモ)](#ディレクトリ構成ただのメモ)
  - [開発するときに(僕が)よく使うコマンド(ただのメモ)](#開発するときに僕がよく使うコマンドただのメモ)
    - [FastAPI](#fastapi)
    - [migration](#migration)
    - [pip package](#pip-package)

## 動かす
### 必要条件
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

http://127.0.0.1:8080/docs でAPIドキュメントが読める

## ディレクトリ構成(ただのメモ)
- app/
  - main.py
    - アプリケーションルート的なやつ
  - database.py
    - SQLAlchemyを使ってDBに接続
  - schemas/
    - Pydamicを使用したスキーマの定義
  - routers/
    - パスオペレーションの実装
  - models/
    - sqlalchemyによるモデル定義(DBとPythonのクラスをつなぐ)
  - cruds/
    - クエリを発行
- db/
  - quaint-api-app.db
    - SQLiteのデータベースを置いておく。（将来的にはSQLサーバーに変更して消そう）
- migration/
  - alembic init migration で生成されたファイル

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
### pip package
このディレクトリ以下で使ってるパッケージだけをrequirements.txtに記録
```sh
$ pipreqs . --force
```