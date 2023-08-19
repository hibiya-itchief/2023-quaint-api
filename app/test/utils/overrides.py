import os

from app.db import dbsettings, get_db
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URI = "mysql://"+ dbsettings.mysql_user +":"+ dbsettings.mysql_password +"@"+ dbsettings.db_host +"/quaint-app-test"

engine = create_engine(TEST_DATABASE_URI)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
