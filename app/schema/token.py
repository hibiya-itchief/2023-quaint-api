from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel

from app import schemas

class Token(BaseModel):
    access_token:str
    token_type:str
class TokenData(BaseModel):#JWTに含まれるデータ
    username: Union[str,None] = None