from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel

from app import schemas

class TagBase(BaseModel):
    tagname:str=Query(max_length=200)
class Tag(TagBase):
    id:str#hashids
    groups:List[schemas.group.Group]
    class Config:
        orm_mode=True