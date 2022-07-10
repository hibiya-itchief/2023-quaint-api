from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import schemas

from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel


class Token(BaseModel):
    access_token:str
    token_type:str
class TokenData(BaseModel):#JWTに含まれるデータ
    username: Union[str,None] = None