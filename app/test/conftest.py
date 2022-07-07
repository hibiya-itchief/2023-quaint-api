from typing import Generator
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker
from sqlalchemy_utils import database_exists, create_database


from app.config import settings
from app.database import Base
from app.main import app

from app.test.utils.overrides import TestingSessionLocal,engine

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    if not database_exists(settings.DATABASE_URI):
        create_database(settings.DATABASE_URI)

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)