# quaint-api
星陵祭オンライン整理券システム「QUAINT」のバックエンドAPI
## 目次
- [quaint-api](#quaint-api)
  - [目次](#目次)
  - [動かす](#動かす)
    - [必要要件](#必要要件)
  - [ディレクトリ構成(ただのメモ)](#ディレクトリ構成ただのメモ)

## 動かす
Gitリポジトリをクローン
```sh
git clone https://github.com/hibiya-itchief/quaint-api.git
```
使用するパッケージをrequirements.txt(まだない)でインストール
```
pip install -r requirements.txt
```
サーバーをスタート
```
uvicorn main:app --reload
```
http://127.0.0.1:8000/docs でAPIドキュメントが読める

### 必要要件
おそらく
- Python 3.6+
- pip 

で動く


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
