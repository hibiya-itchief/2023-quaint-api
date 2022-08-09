from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    db_user:str
    db_password:str
    db_host:str

    HASHIDS_SALT = os.environ["QUAINT_HASHIDS_SALT"]

    class Config:
        env_file = '../.env'
        secrets_dir='/run/secrets'

settings= Settings()