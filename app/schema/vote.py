from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel

from app import schemas

class VoteModel(BaseModel):
    group_id:str#hashids
    user_id:str#hashids
class Vote(VoteModel):
    id:str#hashids