from pydantic import BaseSettings
import os
import datetime

class Settings(BaseSettings):
    mysql_user:str=os.getenv('MYSQL_USER')
    mysql_password:str=os.getenv('MYSQL_PASSWORD')
    db_host:str=os.getenv('DB_HOST')

    login_jwt_secret:str=os.getenv('LOGIN_JWT_SECRET')

    #Oracle Object Storage
    region_name:str=os.getenv('REGION_NAME',"")
    aws_secret_access_key:str=os.getenv('AWS_SECRET_ACCESS_KEY',"")
    aws_access_key_id:str=os.getenv('AWS_ACCESS_KEY_ID',"")
    endpoint_url:str=os.getenv('ENDPOINT_URL',"")

    # Parameter
    ## JWT EXPIRE
    access_token_expire:datetime.timedelta=datetime.timedelta(days=10)

    class Config:
        env_file = '../.env'
        secrets_dir='/run/secrets'

settings= Settings()