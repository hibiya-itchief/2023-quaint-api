# quaint-api
星陵祭オンライン整理券システム「QUAINT」のバックエンドAPI
## 目次
- [quaint-api](#quaint-api)
  - [目次](#目次)
  - [動かす](#動かす)
    - [必要条件](#必要条件)
    - [手順](#手順)
  - [ディレクトリ構成(ただのメモ)](#ディレクトリ構成ただのメモ)

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
- app
  - schemas
    - Pydamicを使用したスキーマの定義
  - routers
    - パスオペレーションの実装
  - models
    - sqlalchemyによるモデル定義(DBとPythonのクラスをつなぐ)
  - cruds
    - クエリを発行
