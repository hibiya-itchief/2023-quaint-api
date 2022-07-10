from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URI = "mysql://quaint:password@localhost/quaint-app"
    TEST_DATABASE_URI = "mysql://quaint:password@localhost/quaint-app-test"
    #HASHIDS_SALT = os.environ["HASHIDS_SALT"]
    HASHIDS_SALT = "wetrfhixcrycyk"
settings= Settings()