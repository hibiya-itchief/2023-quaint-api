from datetime import datetime
from enum import Enum
from typing import List, Literal, Union

from fastapi import Query
from pydantic import BaseModel, Field


class EventTarget(str,Enum):
    guest = "guest"
    visited = "visited"
    school = "school"

class EventBase(BaseModel):
    eventname:str

    lottery:bool=False

    target:EventTarget
    ticket_stock:int
class EventCreate(EventBase):
    starts_at:datetime
    ends_at:datetime
    sell_starts:datetime
    sell_ends:datetime
class EventDBInput(EventBase):
    starts_at:str
    ends_at:str
    sell_starts:str
    sell_ends:str
class Event(EventCreate):
    id:str#ULID
    group_id:str#ULID
    class Config:
        orm_mode=True
class EventDBOutput(EventDBInput):
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
    title:Union[str,None] = Query(default=None,max_length=200)
    description:Union[str,None] = Query(default=None,max_length=200)
    twitter_url:Union[str,None]=Query(default=None,regex="https?://twitter\.com/[0-9a-zA-Z_]{1,15}/?")
    instagram_url:Union[str,None]=Query(default=None,regex="https?://instagram\.com/[0-9a-zA-Z_.]{1,30}/?")
    stream_url:Union[str,None]=Query(default=None,regex="https?://web\.microsoftstream\.com/video/[\w!?+\-_~=;.,*&@#$%()'[\]]+/?")
    public_thumbnail_image_url:Union[str,None]=Query(default=None,max_length=200)
    public_page_content_url:Union[str,None] = Query(default=None,max_length=200)
    private_page_content_url:Union[str,None] = Query(default=None,max_length=200)
class GroupBase(GroupUpdate):#userdefined idをURLにする。groupnameは表示名
    id:str=Query(regex="^[a-zA-Z0-9_\-.]{3,16}$",min_length=3,max_length=16)
    groupname:str = Query(max_length=200)
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
    status:Literal["active","active","cancelled","used","pending","reject"] #https://github.com/hibiya-itchief/quaint-api/issues/91

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
    sub:str
    oid:Union[str,None]
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
    note:Union[str,None]
    class Config:
        orm_mode=True

class GAScreenPageViewResponse(BaseModel):
    start_date:str
    end_date:str
    page_path:str
    view:int


Event.update_forward_refs()
Group.update_forward_refs()
Tag.update_forward_refs()
Ticket.update_forward_refs()

def EventDBOutput_fromEvent(e:Event):
    return EventDBOutput(
        eventname=e.eventname,
        lotterry=e.lottery,
        target=e.target,
        ticket_stock=e.ticket_stock,
        starts_at=e.starts_at.isoformat(),
        ends_at=e.ends_at.isoformat(),
        sell_starts=e.sell_starts.isoformat(),
        sell_ends=e.sell_ends.isoformat(),
        id=e.id,
        group_id=e.group_id
    )
