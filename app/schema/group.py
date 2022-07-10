from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel

from app import schemas

class GroupBase(BaseModel):#hashidsのidをURLにする。groupnameは表示名
    groupname:str = Query(max_length=200)
    title:Union[str,None] = Query(default=None,max_length=200)
    description:Union[str,None] = Query(default=None,max_length=200)
    page_content:Union[str,None] = Query(default=None,max_length=65500)
    enable_vote:bool = True
class GroupCreate(GroupBase):
    pass
class Group(GroupBase):
    id:str#hashids
    events:List[schemas.event.Event]
    users:List[schemas.user.User]
    tags:List[schemas.tag.Tag]
    votes:List[schemas.vote.Vote]
    class Config:
        orm_mode=True