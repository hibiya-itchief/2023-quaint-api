from factory.alchemy import SQLAlchemyModelFactory

from app import models
from app import schemas
from app.test.utils.overrides import TestingSessionLocal

class Admin_UserCreateByAdmin():
    username = "admin"
    password = "password"
    is_student=True
    is_family=False
    is_active=False
    password_expired=False

class hogehoge_UserCreateByAdmin():
    username = "hoge_hoge"
    password = "password"
    is_student=False
    is_family=False
    is_active=False
    password_expired=False
class tag1_TagCreateByAdmin():
    tagname="タグ1"
    
