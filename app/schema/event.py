from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel
from app import schemas

class EventBase(BaseModel):
    title:str=Query(max_length=200)
    description:str=Query(max_length=200)
    sell_at:datetime
    sell_ends=datetime
    starts_at:datetime
    ends_at:datetime
    ticket_stock:int
    lottery:bool=False
    group_id:str#hashids
class EventCreate(EventBase):
    pass
class Event(EventBase):#後夜祭対策でプログラム毎に名前とか入れれるように・抽選か先着か決める
    id:str#hashids
    group:List[schemas.group.Group]
    tickets:List[schemas.ticket.Ticket]
    class Config:
        orm_mode=True