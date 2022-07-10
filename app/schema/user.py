from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel

from app import schemas

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
    id : str#hashids
    
    is_student:bool=False
    is_family:bool=False
    is_active:bool=False
    password_expired: bool=True

    tickets: List[schemas.ticket.Ticket]=[]
    groups: List[schemas.group.Group]=[]
    votes: List[schemas.user.User]=[]

    class Config:
        orm_mode=True

class PasswordChange(UserCreate):
    new_password:str=Query(min_length=6,regex="^[0-9a-zA-Z]*$",max_length=255)
