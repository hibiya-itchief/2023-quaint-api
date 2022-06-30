from datetime import datetime
from typing import List, Union

from pydantic import BaseModel


class GroupBase(BaseModel):
    groupname:str
    title:str
    description:str
class GroupCreate(GroupBase):
    pass
class Group(GroupBase):
    id:int
    #programs:List[Program]
    #users:List[User]
    class Config:
        orm_mode=True

class ProgramBase(BaseModel):
    sell_at:datetime
    starts_at:datetime
    ends_at:datetime
    ticket_stock:int
    group_id:int
class ProgramCreate(ProgramBase):
    pass
class Program(ProgramBase):
    id:int
    group:List[Group]
    #tickets:List[Ticket]
    class Config:
        orm_mode=True

class TicketBase(BaseModel):
    program_id:int
    owner_id:int
    is_family_ticket:bool = False
class TicketCreate(TicketBase):
    pass
class Ticket(TicketBase):
    id:int
    created_at:int
    is_used:bool
    program:List[Program]
    #owner:List[User]
    class Config:
        orm_mode=True

class UserBase(BaseModel):
    username: str
    is_family:bool=False
    is_active:bool=False
    password_expired: bool=True
class UserCreate(UserBase):
    password: str
class User(UserBase):
    id : int
    
    tickets: List[Ticket]=[]
    groups: List[Group]=[]
    
    class Config:
        orm_mode=True