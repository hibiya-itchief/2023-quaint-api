from datetime import datetime

from app import crud, schemas, models
from app.main import app
from app.test import factories
from fastapi.testclient import TestClient
from requests import Session
from typing_extensions import assert_type

client = TestClient(app)

#crud.pyの関数の順番順にテストを書いていく
#一部のテストは実装していない(特にJWTトークンが絡む部分)

def test_time_overlap():
    #重なっている場合1
    start1 = datetime(year=2024, month=9, day=12,hour=8,minute=30)
    end1 = datetime(year=2024, month=9,day=12,hour=9,minute=30)
    start2 = datetime(year=2024, month=9,day=12,hour=8,minute=45)
    end2 = datetime(year=2024, month=9,day=12,hour=9,minute=45)
    assert crud.time_overlap(start1, end1, start2, end2) == True

    #重なっている場合2
    start3 = datetime(year=2024, month=9,day=12,hour=8,minute=30)
    end3 = datetime(year=2024, month=9,day=12,hour=9,minute=30)
    start4 = datetime(year=2024, month=9,day=12,hour=8,minute=35)
    end4 = datetime(year=2024, month=9,day=12,hour=9,minute=25)
    assert crud.time_overlap(start3, end3, start4, end4) == True

    #重なっている場合3
    start5 = datetime(year=2024, month=9,day=12,hour=9,minute=30)
    end5 = datetime(year=2024, month=9,day=12,hour=10,minute=30)
    start6 = datetime(year=2024, month=9,day=12,hour=8,minute=35)
    end6 = datetime(year=2024, month=9,day=12,hour=9,minute=45)
    assert crud.time_overlap(start5, end5, start6, end6) == True

    #重なっていない場合
    start7 = datetime(year=2024, month=9,day=12,hour=8,minute=30)
    end7 = datetime(year=2024, month=9,day=12,hour=9,minute=30)
    start8 = datetime(year=2024, month=9,day=12,hour=9,minute=35)
    end8 = datetime(year=2024, month=9,day=12,hour=10,minute=25)
    assert crud.time_overlap(start7, end7, start8, end8) == False

def test_create_group(db):
    crud.create_group(db, factories.group1)

    #追加したidに一致するオブジェクトが格納されている
    assert db.query(models.Group).filter(models.Group.id == factories.group1.id) != None

#これは何をテストするべき？
def test_get_all_groups_public(db):
    pass

#これは何をテストするべき？
def test_get_group_public(db):
    pass

#改善が必要
def test_update_group(db):
    crud.create_group(db, factories.group1)
    res_group = crud.update_group(db, factories.group1, factories.group1_update)
    assert res_group != None

def test_change_public_thumbnail_image_url(db):
    crud.create_group(db, factories.group1)
    res_group = crud.change_public_thumbnail_image_url(db, factories.group1, 'abcdefg')

    assert res_group.public_thumbnail_image_url == 'abcdefg'

