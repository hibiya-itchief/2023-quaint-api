from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import schemas

from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel


class VoteModel(BaseModel):
    group_id:str#hashids
    user_id:str#hashids
class Vote(VoteModel):
    id:str#hashids