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

    id = Column(Integer,primary_key=True,index=True,autoincrement=True)

    title = Column(VARCHAR(255),nullable=False) #Groupのtitleを継承
    description = Column(VARCHAR(255),nullable=False) # Groupのdescriptionを継承

    sell_at = Column(DateTime,nullable=False)
    sell_ends = Column(DateTime,nullable=False)
    starts_at = Column(DateTime,nullable=False)
    ends_at = Column(DateTime,nullable=False)

    ticket_stock = Column(Integer,nullable=False)#0でチケット機能を使わない

    lottery = Column(Boolean,default=False,nullable=False) # True:抽選 False:先着
    group_id = Column(Integer, ForeignKey("groups.id"),nullable=False)

    group = relationship("Group",back_populates="events")
    tickets = relationship("Ticket",back_populates="events")

class Admin(Base):
    __tablename__ = "admin"
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False,primary_key=True)


class Authority(Base):
    #UserとGroupを結びつける中間テーブル権限管理
    __tablename__ = "authority"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)

    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    group_id = Column(Integer,ForeignKey("groups.id"),nullable=False)

    role = Column(VARCHAR(255))

class GroupTag(Base):
    __tablename__="grouptag"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)

    group_id = Column(Integer,ForeignKey("groups.id"),nullable=False)
    tag_id = Column(Integer,ForeignKey("tags.id"),nullable=False)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    tagname = Column(VARCHAR(255),unique=True,nullable=False)

    groups = relationship("Group",secondary=GroupTag.__tablename__,back_populates="tags")

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    group_id = Column(Integer,ForeignKey("groups.id"),nullable=False)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)

    groups = relationship("Group",back_populates="votes")
    users = relationship("User",back_populates="votes")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)

    groupname = Column(VARCHAR(255), index=True,nullable=False)#団体名

    title = Column(VARCHAR(255))#演目名
    description = Column(VARCHAR(255))#説明(一覧になったときに出る・イベントのデフォルトに使われる)

    page_content = Column(TEXT(16383))#宣伝ページのHTML

    enable_vote = Column(Boolean,default=True)#投票機能を使うか


    events = relationship("Event",back_populates="group")
    users = relationship("User",secondary=Authority.__tablename__,back_populates="groups")
    tags = relationship("Tag",secondary=GroupTag.__tablename__,back_populates="groups")
    votes = relationship("Vote",back_populates="groups")
    

class Ticket(Base):
    __tablename__ = "tickets"

    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    created_at = Column(Timestamp,server_default=current_timestamp())

    event_id = Column(Integer, ForeignKey("events.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    person = Column(Integer,default=1)#何人分のチケットか

    is_family_ticket = Column(Boolean,default=False)#家族の1枚保証制度で取られたチケットかどうか
    is_used = Column(Boolean,default=False)

    events = relationship("Event", back_populates="tickets")
    owner = relationship("User", back_populates="tickets")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)

    username = Column(VARCHAR(25), unique=True, index=True)
    hashed_password = Column(VARCHAR(255))

    is_student = Column(Boolean,default=False)#生徒かどうか
    is_family = Column(Boolean,default=False)#家族アカウントかどうか
    is_active = Column(Boolean, default=False)#学校にいるか
    password_expired=Column(Boolean,default=False)#Password変更を要求

    tickets = relationship("Ticket",back_populates="owner")
    groups = relationship("Group",secondary=Authority.__tablename__,back_populates="users")
    votes = relationship("Vote",back_populates="users")
