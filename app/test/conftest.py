from typing import Generator

import pytest
from app.db import Base, dbsettings
from app.main import app
from app.test.utils.overrides import TestingSessionLocal, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

DATABASE_URI = "mysql://"+ dbsettings.mysql_user +":"+ dbsettings.mysql_password +"@"+ dbsettings.db_host +"/quaint-app"

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    if not database_exists(DATABASE_URI):
        create_database(DATABASE_URI)

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
