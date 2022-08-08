from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URI = "mysql://"+os.environ["QUAINT_DB_USER"]+":"+os.environ["QUAINT_DB_PASSWORD"]+"@"+os.environ['QUAINT_DB_HOST']+"/quaint-app"
    TEST_DATABASE_URI = "mysql://"+os.environ["QUAINT_DB_USER"]+":"+os.environ["QUAINT_DB_PASSWORD"]+"@"+os.environ['QUAINT_DB_HOST']+"/quaint-app-test"
    HASHIDS_SALT = os.environ["QUAINT_HASHIDS_SALT"]
settings= Settings()