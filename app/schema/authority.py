from datetime import datetime
from typing import List, Union
from fastapi import Query
from enum import Enum

from pydantic import BaseModel

from app import schemas


class AuthorityRole(str,Enum):
    Authorizer = "Authorizer"
    Owner = "Owner"
    Admin = "Admin"
