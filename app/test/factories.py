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
class passwordexpired_UserCreateByAdmin():
    username = "hoge_hoge"
    password = "password"
    is_student=False
    is_family=False
    is_active=False
    password_expired=True
class active_UserCreateByAdmin():
    username = "active_hoge_hoge"
    password = "password"
    is_student=False
    is_family=False
    is_active=True
    password_expired=False
class inactive_UserCreateByAdmin():
    username = "active_hoge_hoge"
    password = "password"
    is_student=False
    is_family=False
    is_active=False
    password_expired=False
class active_student_UserCreateByAdmin():
    username = "active_hoge_hoge"
    password = "password"
    is_student=True
    is_family=False
    is_active=True
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
    enable_vote=True
    twitter_url=None
    instagram_url=None
    stream_url=None
    public_thumbnail_image_url=None    
    public_page_content_url="<html><h1>宣伝ページ</h1></html>"
    private_page_content_url="<html><h1>プライベート</h1></html>"
    floor=1
    place="社会科教室"
class group2_GroupCreateByAdmin():
    id="18R"
    groupname="2年8組"
    title="あああああ"
    description="ここに説明文"
    enable_vote=False
    twitter_url=None
    instagram_url=None
    stream_url=None
    public_thumbnail_image_url=None
    public_page_content_url="<html><h1>宣伝ページ</h1></html>"
    private_page_content_url="<html><h1>プライベート</h1></html>"
    cover_image_url=None
    floor=2
    place="生徒ホール"

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

# 変数
group1 = schemas.GroupCreate(
    id="28r",
    groupname="2年8組",
    title="SING",
    description="ここに説明文",
    enable_vote=True,
    twitter_url=None,
    instagram_url=None,
    stream_url=None,
    public_thumbnail_image_url=None,
    public_page_content_url="<html><h1>宣伝ページ</h1></html>",
    private_page_content_url="<html><h1>プライベート</h1></html>",
    floor=1,
    place="社会科教室",
)

group2 = schemas.GroupCreate(
    id="17r",
    groupname="1年7組",
    title="hatopoppo",
    description="ここに説明文",
    enable_vote=True,
    twitter_url=None,
    instagram_url=None,
    stream_url=None,
    public_thumbnail_image_url=None,
    public_page_content_url="<html><h1>宣伝ページ</h1></html>",
    private_page_content_url="<html><h1>プライベート</h1></html>",
    floor=2,
    place="生徒ホール",
)

# 変数
group3 = schemas.GroupCreate(
    id="test_1",
    groupname="テストグループ",
    title="TEST_TEST",
    description="TESTです",
    enable_vote=True,
    twitter_url=None,
    instagram_url=None,
    stream_url=None,
    public_thumbnail_image_url=None,
    public_page_content_url="<html><h1>宣伝ページ</h1></html>",
    private_page_content_url="<html><h1>プライベート</h1></html>",
    floor=4,
    place="LL教室",
)

group1_update = schemas.GroupUpdate(
    id="28r",
    groupname="2年8組",
    title="sample",
    description="ここに説明文",
    enable_vote=True,
    twitter_url=None,
    instagram_url=None,
    stream_url=None,
    public_thumbnail_image_url=None,
    public_page_content_url="<html><h1>宣伝ページ</h1></html>",
    private_page_content_url="<html><h1>プライベート</h1></html>",
    floor=3,
    place="生徒ホール",
)

group_tag_create1 = schemas.GroupTagCreate(
    tag_id='test'
)