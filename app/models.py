#from numpy import integer
#from pandas import notnull
from sqlalchemy import (TEXT, TIMESTAMP, VARCHAR, Boolean, Column, DateTime,
                        ForeignKey, Integer, String, UniqueConstraint)
from sqlalchemy.orm import relationship
# from sqlalchemy.dialects.mysql import TIMESTAMP as Timestamp
from sqlalchemy.sql.functions import current_timestamp

from app.db import Base


class ReadAuthority(Base):
    __tablename__ = "readauthority"

    id = Column(VARCHAR(255),primary_key=True,index=True,unique=True)#ULID
    name = Column(VARCHAR(255),nullable=False)
    idp = Column(VARCHAR(255),nullable=False)
    b2c_visited = Column(Boolean)
    ad_group = Column(VARCHAR(255))
    __table_args__ = (UniqueConstraint("idp", "b2c_visited","ad_group", name="unique_idpx_b2c_visited_ad_group"),)

class EventReadAuthority(Base):
    __tablename__ = "eventreadauthority"
    id = Column(VARCHAR(255),primary_key=True,index=True,unique=True)#ULID
    event_id = Column(VARCHAR(255), ForeignKey("events.id"),nullable=False)
    readauthority_id = Column(VARCHAR(255), ForeignKey("readauthority.id"),nullable=False)
    __table_args__ = (UniqueConstraint("event_id", "readauthority_id", name="unique_idx_eventid_readauthorityid"),)

class Event(Base):
    __tablename__ = "events"

    id = Column(VARCHAR(255),primary_key=True,index=True,unique=True)#ULID
    group_id = Column(VARCHAR(255), ForeignKey("groups.id"),nullable=False)
    eventname = Column(VARCHAR(255))

    # 日時はISO 8601形式で文字列として保存 MySQLによって勝手にタイムゾーンをいじられたり保存されなかったりしたくない
    starts_at = Column(VARCHAR(255),nullable=False)
    ends_at = Column(VARCHAR(255),nullable=False)
    sell_starts = Column(VARCHAR(255),nullable=False)
    sell_ends = Column(VARCHAR(255),nullable=False)

    lottery = Column(Boolean)

    ticket_stock = Column(Integer,nullable=False)#0でチケット機能を使わない 

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
    user_id = Column(VARCHAR(255),nullable=False,primary_key=True)# sub in jwt (UUID)


class Group(Base):
    __tablename__ = "groups"
    id = Column(VARCHAR(255), primary_key=True, index=True,unique=True)#user defined unique id

    groupname = Column(VARCHAR(255), index=True,nullable=False)#団体名

    title = Column(VARCHAR(255))#演目名
    description = Column(VARCHAR(255))#説明(一覧になったときに出る・イベントのデフォルトに使われる)

    enable_vote = Column(Boolean,default=True)#投票機能を使うか
    twitter_url = Column(VARCHAR(255))
    instagram_url = Column(VARCHAR(255))
    stream_url = Column(VARCHAR(255))

    public_thumbnail_image_url=Column(VARCHAR(255))#オブジェクトストレージ上の公開団体サムネイル画像へのURL
    public_page_content_url = Column(VARCHAR(255))#オブジェクトストレージ上の団体個別公開ページのMarkdownへのURL
    private_page_content_url = Column(VARCHAR(255))#オブジェクトストレージ上の団体個別非公開ページのMarkdownへのURL
    def update_dict(self,dict):
        print(dict)
        for name, value in dict.items():
            if name in self.__dict__ :
                setattr(self, name, value)
    
class GroupOwner(Base):
    __tablename__ = "groupowners"
    group_id=Column(VARCHAR(255), ForeignKey("groups.id"),primary_key=True)
    user_id=Column(VARCHAR(255),primary_key=True) # sub in jwt (UUID)
    note=Column(VARCHAR(255)) # note for management use
    UniqueConstraint('group_id', 'user_id', name="unique_idx_groupid_userid")

class Ticket(Base):
    __tablename__ = "tickets"

    id=Column(VARCHAR(255),primary_key=True,index=True,unique=True)#ULID
    created_at = Column(VARCHAR(255))

    group_id = Column(VARCHAR(255), ForeignKey("groups.id"))
    event_id = Column(VARCHAR(255), ForeignKey("events.id"))
    owner_id = Column(VARCHAR(255))# sub in jwt (UUID)

    person = Column(Integer,default=1)#何人分のチケットか

    is_family_ticket = Column(Boolean,default=False)#家族の1枚保証制度で取られたチケットかどうか
    is_used = Column(Boolean,default=False)



