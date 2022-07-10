from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import schemas

from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel

class AuthorityRole(str,Enum):
    Authorizer = "Authorizer"
    Owner = "Owner"
    Admin = "Admin"
