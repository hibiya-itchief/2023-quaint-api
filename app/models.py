#from numpy import integer
#from pandas import notnull
from sqlalchemy import TEXT, VARCHAR, Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.dialects.sqlite import TIMESTAMP as Timestamp
# from sqlalchemy.dialects.mysql import TIMESTAMP as Timestamp
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.orm import relationship

from .database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(VARCHAR(255),primary_key=True,index=True,unique=True)#ULID

    title = Column(VARCHAR(255),nullable=False) #Groupのtitleを継承
    description = Column(VARCHAR(255),nullable=False) # Groupのdescriptionを継承

    sell_at = Column(DateTime,nullable=False)
    sell_ends = Column(DateTime,nullable=False)
    starts_at = Column(DateTime,nullable=False)
    ends_at = Column(DateTime,nullable=False)

    ticket_stock = Column(Integer,nullable=False)#0でチケット機能を使わない

    group_id = Column(VARCHAR(255), ForeignKey("groups.id"),nullable=False)


class Admin(Base):
    __tablename__ = "admin"
    user_id = Column(VARCHAR(255),ForeignKey("users.id"),nullable=False,primary_key=True)#ULID

class Entry(Base):
    __tablename__ = "entry"
    user_id = Column(VARCHAR(255),ForeignKey("users.id"),nullable=False,primary_key=True)#ULID

class Authority(Base):
    #UserとGroupを結びつける中間テーブル権限管理
    __tablename__ = "authority"
    id = Column(Integer,unique=True,autoincrement=True,primary_key=True)

    user_id = Column(VARCHAR(255),ForeignKey("users.id"),nullable=False)
    group_id = Column(VARCHAR(255),ForeignKey("groups.id"),nullable=False)

    role = Column(VARCHAR(255))

class GroupTag(Base):
    __tablename__="grouptag"
    id = Column(Integer,unique=True,autoincrement=True,primary_key=True)
    group_id = Column(VARCHAR(255),ForeignKey("groups.id"),nullable=False)
    tag_id = Column(VARCHAR(255),ForeignKey("tags.id"),nullable=False)

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


    

class Ticket(Base):
    __tablename__ = "tickets"

    id=Column(VARCHAR(255),primary_key=True,index=True,unique=True)#ULID
    created_at = Column(DateTime,server_default=current_timestamp())

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

