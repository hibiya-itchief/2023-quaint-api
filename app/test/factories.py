from factory.alchemy import SQLAlchemyModelFactory

import datetime

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
class tag2_TagCreateByAdmin():
    tagname="タグ2"
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

class Timetable():
    timetablename:str
    sell_at:datetime
    sell_ends:datetime
    starts_at:datetime
    ends_at:datetime
class valid_timetable1(Timetable):
    timetablename="1日目 - 第1公演"
    sell_at=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=0,second=0))
    sell_ends=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=30,second=0))
    starts_at=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=30,second=0))
    ends_at=str(datetime.datetime(year=2022,month=9,day=17,hour=10,minute=30,second=0))
class valid_timetable2(Timetable):
    timetablename="1日目 - 第2公演"
    sell_at=str(datetime.datetime(year=2022,month=9,day=17,hour=10,minute=0,second=0))
    sell_ends=str(datetime.datetime(year=2022,month=9,day=17,hour=10,minute=30,second=0))
    starts_at=str(datetime.datetime(year=2022,month=9,day=17,hour=10,minute=30,second=0))
    ends_at=str(datetime.datetime(year=2022,month=9,day=17,hour=11,minute=30,second=0))

class invalid_timetable1():
    timetablename="1日目 - 第1公演"
    sell_at=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=30,second=0))
    sell_ends=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=0,second=0))
    starts_at=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=30,second=0))
    ends_at=str(datetime.datetime(year=2022,month=9,day=17,hour=10,minute=30,second=0))

class invalid_timetable2():
    timetablename="1日目 - 第1公演"
    sell_at=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=0,second=0))
    sell_ends=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=30,second=0))
    starts_at=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=20,second=0))
    ends_at=str(datetime.datetime(year=2022,month=9,day=17,hour=10,minute=30,second=0))

class invalid_timetable3():
    timetablename="1日目 - 第1公演"
    sell_at=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=0,second=0))
    sell_ends=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=30,second=0))
    starts_at=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=30,second=0))
    ends_at=str(datetime.datetime(year=2022,month=9,day=17,hour=9,minute=0,second=0))

