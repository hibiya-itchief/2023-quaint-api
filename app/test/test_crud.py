from datetime import datetime

from app import crud, schemas, models
from app.main import app
from app.test import factories

from fastapi import HTTPException
from fastapi.testclient import TestClient
from requests import Session
from typing_extensions import assert_type
import pytest
import pandas as pd

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

def test_add_tag(db):
    tag = factories.group_tag_create1
    db_tag = models.Tag(id=tag.tag_id, tagname='sample')
    db_group = models.Group(**factories.group1.dict())

    #テスト用のgroupをDBに追加
    db.add(db_group)
    db.add(db_tag)
    db.commit()
    db.refresh(db_group)

    #指定された団体が存在しない
    assert crud.add_tag(db, factories.group2.id, tag) == None

    #存在しないタグを追加
    assert crud.add_tag(db, factories.group1.id, schemas.GroupTagCreate(tag_id='sample')) == None

    #重複していないタグを追加
    assert crud.add_tag(db, factories.group1.id, tag)  != None

    #重複しているタグを追加
    with pytest.raises(HTTPException) as err:
        crud.add_tag(db, factories.group1.id, tag)
    assert err.value.status_code == 200
    assert err.value.detail == 'Already Registed'

def test_check_df(db):
    correct_df = pd.read_csv(filepath_or_buffer='/workspace/csv/sample-sheet.csv')
    incorrect_title_df = pd.read_csv(filepath_or_buffer='/workspace/csv/incorrect-title-sheet.csv')
    incorrect_groupid_df = pd.read_csv(filepath_or_buffer='/workspace/csv/incorrect-groupid-sheet.csv')
    incorrect_time_df = pd.read_csv(filepath_or_buffer='/workspace/csv/incorrect-time-sheet.csv')

    group = factories.group3
    crud.create_group(db, group)

    assert crud.check_df(db,correct_df) == None

    with pytest.raises(HTTPException) as err1:
        crud.check_df(db,incorrect_title_df)
    assert err1.value.status_code == 422
    assert err1.value.detail == 'カラム名が正しいことを確認してください。'

    with pytest.raises(HTTPException) as err2:
        crud.check_df(db,incorrect_groupid_df)
    assert err2.value.status_code == 400
    assert err2.value.detail == '存在しないgroup_idが含まれています。'

    with pytest.raises(HTTPException) as err3:
        crud.check_df(db,incorrect_time_df)
    assert err3.value.status_code == 422
    assert err3.value.detail == '時刻の表記方法が正しいことを確認してください。'
