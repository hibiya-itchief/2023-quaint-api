#from numpy import integer
#from pandas import notnull
from sqlalchemy import TEXT, VARCHAR, Boolean, Column, ForeignKey, Integer, String, DateTime,UniqueConstraint
from sqlalchemy.dialects.sqlite import TIMESTAMP as Timestamp
# from sqlalchemy.dialects.mysql import TIMESTAMP as Timestamp
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.orm import relationship

from .database import Base


class Timetable(Base):
    __tablename__ = "timetable"

    id = Column(VARCHAR(255),primary_key=True,index=True,unique=True)#ULID
    timetablename = Column(VARCHAR(255))

    sell_at = Column(DateTime,nullable=False)
    sell_ends = Column(DateTime,nullable=False)
    starts_at = Column(DateTime,nullable=False)
    ends_at = Column(DateTime,nullable=False)

class Event(Base):
    __tablename__ = "events"

    id = Column(VARCHAR(255),primary_key=True,index=True,unique=True)#ULID

    timetable_id = Column(VARCHAR(255),ForeignKey("timetable.id"),nullable=False)

    ticket_stock = Column(Integer,nullable=False)#0でチケット機能を使わない
    lottery = Column(Boolean)
    group_id = Column(VARCHAR(255), ForeignKey("groups.id"),nullable=False)

    # 複数カラムのunique constraint
    __table_args__ = (UniqueConstraint("timetable_id", "group_id", name="unique_timetablex_groupid"),)

class Admin(Base):
    __tablename__ = "admin"
    user_id = Column(VARCHAR(255),ForeignKey("users.id"),nullable=False,primary_key=True,unique=True)#ULID

class Entry(Base):
    __tablename__ = "entry"
    user_id = Column(VARCHAR(255),ForeignKey("users.id"),nullable=False,primary_key=True,unique=True)#ULID

class Authority(Base):
    #UserとGroupを結びつける中間テーブル権限管理
    __tablename__ = "authority"
    user_id = Column(VARCHAR(255),ForeignKey("users.id"),nullable=False,primary_key=True)
    group_id = Column(VARCHAR(255),ForeignKey("groups.id"),nullable=False,primary_key=True)

    role = Column(VARCHAR(255),primary_key=True)
    # 複数カラムのunique constraint
    __table_args__ = (UniqueConstraint("user_id", "group_id","role", name="unique_idx_groupid_tagid"),)

class GroupTag(Base):
    __tablename__="grouptag"
    group_id = Column(VARCHAR(255),ForeignKey("groups.id"),nullable=False,primary_key=True)
    tag_id = Column(VARCHAR(255),ForeignKey("tags.id"),nullable=False,primary_key=True)
    # 複数カラムのunique constraint
    __table_args__ = (UniqueConstraint("group_id", "tag_id", name="unique_idx_groupid_tagid"),)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(VARCHAR(255),primary_key=True,index=True,unique=True)#ULID
    tagname = Column(VARCHAR(255),unique=True,nullable=False)

class Vote(Base):
    __tablename__ = "votes"
    group_id = Column(VARCHAR(255),ForeignKey("groups.id"),nullable=False)#userdefined id
    user_id = Column(VARCHAR(255),ForeignKey("users.id"),nullable=False,primary_key=True)#ULID


class Group(Base):
    __tablename__ = "groups"
    id = Column(VARCHAR(255), primary_key=True, index=True,unique=True)#user defined unique id

    groupname = Column(VARCHAR(255), index=True,nullable=False)#団体名

    title = Column(VARCHAR(255))#演目名
    description = Column(VARCHAR(255))#説明(一覧になったときに出る・イベントのデフォルトに使われる)

    page_content = Column(TEXT(16383))#宣伝ページのHTML

    enable_vote = Column(Boolean,default=True)#投票機能を使うか
    twitter_url = Column(VARCHAR(255))
    instagram_url = Column(VARCHAR(255))
    stream_url = Column(VARCHAR(255))

    thumbnail_image_url=Column(VARCHAR(255))
    cover_image_url=Column(VARCHAR(255))

    

class Ticket(Base):
    __tablename__ = "tickets"

    id=Column(VARCHAR(255),primary_key=True,index=True,unique=True)#ULID
    created_at = Column(DateTime,server_default=current_timestamp())

    group_id = Column(VARCHAR(255), ForeignKey("groups.id"))
    event_id = Column(VARCHAR(255), ForeignKey("events.id"))
    owner_id = Column(VARCHAR(255), ForeignKey("users.id"))

    person = Column(Integer,default=1)#何人分のチケットか

    is_family_ticket = Column(Boolean,default=False)#家族の1枚保証制度で取られたチケットかどうか
    is_used = Column(Boolean,default=False)


class User(Base):
    __tablename__ = "users"
    id = Column(VARCHAR(255), primary_key=True, index=True,unique=True)#ULID

    username = Column(VARCHAR(25), unique=True, index=True)
    hashed_password = Column(VARCHAR(255))

    is_student = Column(Boolean,default=False)#生徒かどうか
    is_family = Column(Boolean,default=False)#家族アカウントかどうか
    is_active = Column(Boolean, default=False)#学校にいるか
    password_expired=Column(Boolean,default=False)#Password変更を要求

class Log(Base):
    __tablename__ = "log"
    id = Column(Integer,autoincrement=True,primary_key=True,index=True,unique=True)
    timestamp = Column(DateTime,server_default=current_timestamp())
    user = Column(VARCHAR(255))
    object = Column(VARCHAR(255))
    operation = Column(TEXT(30000))
    result =Column(Boolean)
    detail = Column(VARCHAR(255))