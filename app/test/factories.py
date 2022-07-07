from factory.alchemy import SQLAlchemyModelFactory

from app import models,schemas
from app.test.utils.overrides import TestingSessionLocal

class Admin_UserCreateByAdmin():
    username = "admin"
    password = "password"
    is_student=True
    is_family=False
    is_active=False
    password_expired=False

class hogehoge_UserCreateByAdmin():
    username = "hogehoge"
    password = "password"
    is_student=False
    is_family=False
    is_active=False
    password_expired=False
    
