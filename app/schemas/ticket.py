from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import schemas

from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel


class TicketBase(BaseModel):
    event_id:str#hashids
    owner_id:str#hashids
    is_family_ticket:bool = False
    person:int = Query(default=1)#一緒に入場する人数(１人１チケットになったらこれを削除すればdbのdefaultが効く)
class TicketCreate(TicketBase):
    pass
class Ticket(TicketBase):
    id:str#hashids
    created_at:int
    is_used:bool

    events:List[schemas.event.Event]
    owner:List[schemas.user.User]
    class Config:
        orm_mode=True