from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    mysql_user:str
    mysql_password:str
    db_host:str

    login_jwt_secret:str

    #Oracle Object Storage
    region_name:str
    aws_secret_access_key:str
    aws_access_key_id:str
    endpoint_url:str
    class Config:
        env_file = '../.env'
        secrets_dir='/run/secrets'

settings= Settings()