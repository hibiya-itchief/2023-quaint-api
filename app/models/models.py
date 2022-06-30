#from numpy import integer
#from pandas import notnull
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.dialects.sqlite import TIMESTAMP as Timestamp
# from sqlalchemy.dialects.mysql import TIMESTAMP as Timestamp
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.orm import relationship

from app.database import Base


class Authority(Base):
    #UserとGroupを結びつける中間テーブル権限管理
    __tablename__ = "authority"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)

    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    group_id = Column(Integer,ForeignKey("groups.id"),nullable=False)

    role = Column(String(255))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)

    username = Column(String(25), unique=True, index=True)
    hashed_password = Column(String(255))

    is_family = Column(Boolean,default=False)#家族アカウントかどうか

    is_active = Column(Boolean, default=False)#学校にいるか
    password_expired=Column(Boolean,default=False)#Password変更を要求

    tickets = relationship("Ticket",back_populates="owner")
    groups = relationship("Group",secondary=Authority.__tablename__,back_populates="users")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)

    groupname = Column(String(255), index=True)#団体名

    title = Column(String(255))#演目名
    description = Column(String(255))#説明

    programs = relationship("Program",back_populates="group")
    users = relationship("User",secondary=Authority.__tablename__,back_populates="groups")

class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer,primary_key=True,index=True,autoincrement=True)

    sell_at = Column(DateTime)
    starts_at = Column(DateTime)
    ends_at = Column(DateTime)

    ticket_stock = Column(Integer)

    group_id = Column(Integer, ForeignKey("groups.id"))
    group = relationship("Group",back_populates="programs")
    tickets = relationship("Ticket",back_populates="program")

class Ticket(Base):
    __tablename__ = "tickets"

    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    created_at = Column(Timestamp,server_default=current_timestamp())

    program_id = Column(Integer, ForeignKey("programs.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    is_family_ticket = Column(Boolean,default=False)#家族の1枚保証制度で取られたチケットかどうか
    is_used = Column(Boolean,default=False)

    program = relationship("Program", back_populates="tickets")
    owner = relationship("User", back_populates="tickets")

