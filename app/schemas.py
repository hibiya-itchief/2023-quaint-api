from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel




class ProgramBase(BaseModel):
    sell_at:datetime
    starts_at:datetime
    ends_at:datetime
    ticket_stock:int
    group_id:str#hashids
class ProgramCreate(ProgramBase):
    pass
class Program(ProgramBase):#後夜祭対策でプログラム毎に名前とか入れれるように・抽選か先着か決める
    id:str#hashids
    #group:List[Group]
    #tickets:List[Ticket]
    class Config:
        orm_mode=True



class GroupBase(BaseModel):#url形式の英数字と表示名を分けた方がいい
    groupname:str
    title:str
    description:str
class GroupCreate(GroupBase):
    pass
class Group(GroupBase):
    id:str#hashids
    programs:List[Program]
    #users:List[User]
    class Config:
        orm_mode=True


class TicketBase(BaseModel):
    program_id:str#hashids
    owner_id:str#hashids
    is_family_ticket:bool = False
class TicketCreate(TicketBase):
    pass
class Ticket(TicketBase):#一緒に入場する人数
    id:str#hashids
    created_at:int
    is_used:bool
    program:List[Program]
    #owner:List[User]
    class Config:
        orm_mode=True


class UserBase(BaseModel):
    username: str = Query(regex="^[0-9a-zA-Z]*$",min_length=4,max_length=25)
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

    tickets: List[Ticket]=[]
    groups: List[Group]=[]
    
    class Config:
        orm_mode=True

class PasswordChange(UserCreate):
    new_password:str=Query(min_length=6,regex="^[0-9a-zA-Z]*$",max_length=255)




class Token(BaseModel):
    access_token:str
    token_type:str
class TokenData(BaseModel):#JWTに含まれるデータ
    username: Union[str,None] = None

class AuthorityRole(str,Enum):
    Authorizer = "Authorizer"
    Owner = "Owner"
    Admin = "Admin"
