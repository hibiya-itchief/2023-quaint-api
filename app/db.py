import os

from fastapi import HTTPException
from pydantic import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class DBSettings(BaseSettings):
    mysql_user:str=os.getenv('MYSQL_USER')
    mysql_password:str=os.getenv('MYSQL_PASSWORD')
    db_host:str=os.getenv('DB_HOST')
    mysql_database:str=os.getenv('MYSQL_DATABASE')
    class Config:
        env_file = 'app/.env'
        secrets_dir='/run/secrets'
dbsettings=DBSettings()

#SQLALCHEMY_DATABASE_URL = "sqlite:///../db/quaint-api-app.db"
#SQLALCHEMY_DATABASE_URL = "mysql://quaint:password@localhost/quaint-app"

DATABASE_URI = "mysql://"+ dbsettings.mysql_user +":"+ dbsettings.mysql_password +"@"+ dbsettings.db_host +"/"+dbsettings.mysql_database+"?charset=utf8mb4"
engine = create_engine(DATABASE_URI,pool_size=3000,max_overflow=100,pool_timeout=3)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except HTTPException as e:
        raise e
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(503,detail='データベースが混み合っています：  '+e)
    except Exception as e:
        raise e
    finally:
        db.close()
