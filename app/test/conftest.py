from typing import Generator
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker
from sqlalchemy_utils import database_exists, create_database


from app.config import settings
from app.database import Base
from app.main import app

from app.test.utils.overrides import TestingSessionLocal,engine

DATABASE_URI = "mysql://"+ settings.mysql_user +":"+ settings.mysql_password +"@"+ settings.db_host +"/quaint-app"

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    if not database_exists(DATABASE_URI):
        create_database(DATABASE_URI)

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)