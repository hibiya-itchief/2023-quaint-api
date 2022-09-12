from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel,Field

class AuthorityRole(str,Enum):
    Authorizer = "Authorizer"
    Owner = "Owner"
    Admin = "Admin"
    Entry = "Entry"

class TimetableBase(BaseModel):
    timetablename:str=Query(max_length=200)

    sell_at:datetime
    sell_ends:datetime
    starts_at:datetime
    ends_at:datetime
class TimetableCreate(TimetableBase):
    pass
class Timetable(TimetableBase):
    id:str
    class Config:
        orm_mode=True

class EventBase(BaseModel):
    timetable_id:str
    ticket_stock:int
    lottery:bool=False
class EventCreate(EventBase):
    pass
class Event(EventBase):
    id:str#ULID
    group_id:str#ULID
    class Config:
        orm_mode=True

class GroupBase(BaseModel):#userdefined idをURLにする。groupnameは表示名
    id:str=Query(regex="^[a-zA-Z0-9_\-.]{3,16}$",min_length=3,max_length=16)
    groupname:str = Query(max_length=200)
    title:Union[str,None] = Query(default=None,max_length=200)
    description:Union[str,None] = Query(default=None,max_length=200)
    page_content:Union[str,None] = Query(default=None,max_length=16000)
    enable_vote:bool = True
    twitter_url:Union[str,None]=Query(default=None,regex="https?://twitter\.com/[0-9a-zA-Z_]{1,15}/?")
    instagram_url:Union[str,None]=Query(default=None,regex="https?://instagram\.com/[0-9a-zA-Z_.]{1,30}/?")
    stream_url:Union[str,None]=Query(default=None,regex="https?://web\.microsoftstream\.com/video/[\w!?+\-_~=;.,*&@#$%()'[\]]+/?")
class GroupCreate(GroupBase):
    pass
class Group(GroupBase):
    thumbnail_image:Union[str,None] #Base64
    cover_image:Union[str,None]#Base64
    like_num:int
    class Config:
        orm_mode=True

class GroupTagCreate(BaseModel):
    tag_id:str#ULID

class GroupMeLiked(BaseModel):
    me_liked:bool

class TagBase(BaseModel):
    tagname:str=Query(max_length=200)
class TagCreate(TagBase):
    pass
class Tag(TagBase):
    id:str#ULID
    class Config:
        orm_mode=True

class TicketBase(BaseModel):
    group_id:str
    event_id:str#hashids
    owner_id:str#hashids
    is_family_ticket:bool = False
    person:int = Query(default=1)#一緒に入場する人数(１人１チケットになったらこれを削除すればdbのdefaultが効く)
class TicketCreate(TicketBase):
    pass
class Ticket(TicketBase):
    id:str#ULID
    created_at:datetime
    is_used:bool

    class Config:
        orm_mode=True

class TicketsNumberData(BaseModel):
    taken_tickets:int
    left_tickets:int
    stock:int

class Token(BaseModel):
    access_token:str
    token_type:str
class TokenData(BaseModel):#JWTに含まれるデータ
    username: Union[str,None] = None

class UserBase(BaseModel):
    username: str = Query(regex="^[a-zA-Z0-9_\-.]{3,15}$",min_length=4,max_length=25)
class UserCreate(UserBase):
    password: str=Query(min_length=8,regex="^[0-9a-zA-Z]*$",max_length=255)
class UserCreateByAdmin(UserCreate):
    is_student:bool=False
    is_family:bool=False
    is_active:bool=False
    password_expired: bool=True
class User(UserBase):
    id : str#ULID
    
    is_student:bool=False
    is_family:bool=False
    is_active:bool=False
    password_expired: bool=True

    class Config:
        orm_mode=True

class UserAuthority(BaseModel):
    user_id : str#ULID

    is_admin:bool
    is_entry:bool
    owner_of:List[str]
    authorizer_of:List[str]

class PasswordChange(UserCreate):
    new_password:str=Query(min_length=6,regex="^[0-9a-zA-Z]*$",max_length=255)


class VoteBase(BaseModel):
    group_id:str#userdefined id
    user_id:str#ULID
class Vote(VoteBase):
    class Config:
        orm_mode=True

class LogBase(BaseModel):
    timestamp:datetime
    user:Union[str,None]
    object:Union[str,None]
    operation:Union[str,None]
    result:Union[bool,None]
    detail:Union[str,None]
class LogCreate(LogBase):
    pass
class Log(LogBase):
    id:int
    class Config:
        orm_mode=True


Event.update_forward_refs()
Group.update_forward_refs()
Tag.update_forward_refs()
Ticket.update_forward_refs()
User.update_forward_refs()

