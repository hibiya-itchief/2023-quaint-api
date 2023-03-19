from datetime import datetime
from enum import Enum
from typing import List, Union

from fastapi import Query
from pydantic import BaseModel, Field


class EventTarget(str,Enum):
    guest = "guest"
    visited = "visited"
    school = "school"

class EventBase(BaseModel):
    eventname:str

    starts_at:datetime
    ends_at:datetime
    sell_starts:datetime
    sell_ends:datetime

    lottery:bool

    target:EventTarget
    ticket_stock:int
class EventCreate(EventBase):
    pass
class Event(EventBase):
    id:str#ULID
    group_id:str#ULID
    class Config:
        orm_mode=True

class GroupTagCreate(BaseModel):
    tag_id:str#ULID

class TagBase(BaseModel):
    tagname:str=Query(max_length=200)
class TagCreate(TagBase):
    pass
class Tag(TagBase):
    id:str#ULID
    class Config:
        orm_mode=True

class GroupUpdate(BaseModel):
    groupname:Union[str,None] = Query(default=None,max_length=200)
    title:Union[str,None] = Query(default=None,max_length=200)
    description:Union[str,None] = Query(default=None,max_length=200)
    twitter_url:Union[str,None]=Query(default=None,regex="https?://twitter\.com/[0-9a-zA-Z_]{1,15}/?")
    instagram_url:Union[str,None]=Query(default=None,regex="https?://instagram\.com/[0-9a-zA-Z_.]{1,30}/?")
    stream_url:Union[str,None]=Query(default=None,regex="https?://web\.microsoftstream\.com/video/[\w!?+\-_~=;.,*&@#$%()'[\]]+/?")
    public_thumbnail_image_url:Union[str,None]=Query(default=None,max_length=20)
    public_page_content_url:Union[str,None] = Query(default=None,max_length=200)
    private_page_content_url:Union[str,None] = Query(default=None,max_length=200)
class GroupBase(GroupUpdate):#userdefined idをURLにする。groupnameは表示名
    id:str=Query(regex="^[a-zA-Z0-9_\-.]{3,16}$",min_length=3,max_length=16)
    enable_vote:bool = True
    
class GroupCreate(GroupBase):
    class Config:
        orm_mode=True
class Group(GroupBase):
    tags:Union[List[Tag],None]
    class Config:
        orm_mode=True 

class TicketBase(BaseModel):
    group_id:str
    event_id:str#hashids
    owner_id:str# sub in jwt (UUID)
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

class JWTUser(BaseModel):
    aud:Union[str,None]
    iss:Union[str,None]
    iat:Union[int,None]
    nbf:Union[int,None]
    exp:Union[int,None]
    sub:Union[str,None]
    name:Union[str,None]
    jobTitle:Union[str,None]
    groups:Union[List[str],None]
    


class VoteBase(BaseModel):
    group_id:str#userdefined id
    user_id:str# sub in jwt (UUID)
class Vote(VoteBase):
    class Config:
        orm_mode=True

class GroupOwner(BaseModel):
    group_id:str#userdefined id
    user_id:str# sub in jwt (UUID)


Event.update_forward_refs()
Group.update_forward_refs()
Tag.update_forward_refs()
Ticket.update_forward_refs()

