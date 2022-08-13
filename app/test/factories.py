from factory.alchemy import SQLAlchemyModelFactory

from app import models
from app import schemas
from app.test.utils.overrides import TestingSessionLocal

class Admin_UserCreateByAdmin():
    username = "admin"
    password = "password"
    is_student=True
    is_family=False
    is_active=False
    password_expired=False

class hogehoge_UserCreateByAdmin():
    username = "hoge_hoge"
    password = "password"
    is_student=False
    is_family=False
    is_active=False
    password_expired=False
class tag1_TagCreateByAdmin():
    tagname="タグ1"
class group1_GroupCreateByAdmin():
    id="28r"
    groupname="2年8組"
    title="SING"
    description="ここに説明文"
    page_content="<html><h1>宣伝ページ</h1></html>"
    enable_vote=True
    twitter_url=None
    instagram_url=None
    stream_url=None
class group2_GroupCreateByAdmin():
    id="18R"
    groupname="2年8組"
    title="あああああ"
    description="ここに説明文"
    page_content="<html><h1>宣伝ページ</h1></html>"
    enable_vote=True
    twitter_url=None
    instagram_url=None
    stream_url=None
    
