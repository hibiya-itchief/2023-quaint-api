from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    db_user:str
    db_password:str
    db_host:str

    login_jwt_secret:str

    class Config:
        env_file = '.env'
        secrets_dir='/run/secrets'

settings= Settings()