from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
#SQLALCHEMY_DATABASE_URL = "sqlite:///../db/quaint-api-app.db"
#SQLALCHEMY_DATABASE_URL = "mysql://quaint:password@localhost/quaint-app"

DATABASE_URI = "mysql://"+ settings.db_user +":"+ settings.db_password +"@"+ settings.db_host +"/quaint-app"

engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
