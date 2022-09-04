from pydantic import BaseSettings
import os
import datetime

class Settings(BaseSettings):
    mysql_user:str
    mysql_password:str
    db_host:str

    login_jwt_secret:str

    #Oracle Object Storage
    region_name:str=""
    aws_secret_access_key:str=""
    aws_access_key_id:str=""
    endpoint_url:str=""

    # Parameter
    ## JWT EXPIRE
    access_token_expire:datetime.timedelta=datetime.timedelta(days=10)

    class Config:
        env_file = '../.env'
        secrets_dir='/run/secrets'

settings= Settings()