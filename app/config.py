from pydantic import BaseSettings
import os
import datetime

class Parameters(BaseSettings):
    person_per_user:int=3 # 1つのユーザーで同時入場できる人数
    max_tickets:int=6 # 全日程を通して取得できる整理券の上限(0で制限無し)
    max_tickets_per_day:int=6 # 1日あたりの取得できる整理券の上限(0で上限無し)各公演の開始時刻で判定されます

class Settings(BaseSettings):
    mysql_user:str=os.getenv('MYSQL_USER')
    mysql_password:str=os.getenv('MYSQL_PASSWORD')
    db_host:str=os.getenv('DB_HOST')

    jwt_privatekey:str=os.getenv('QUAINT_JWT_PRIVATEKEY')
    jwt_publickey:str="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0i+BMxUUgG6slPW/9oHP\nUrYpoLX08NNTsFpEwAkpBHxzbauFc2SmFaFnmkkco8lfCQs66sj6fwtTtSc4RH+Z\nncFRaxV5M+AS7utyGhS9iNAg6u5DaGAxbMm1NAqUkuNLGS+pVx+p75b681inCBBu\nVxpPF0eCNMsUfMPDBKKKS6ABuIpl4Ep3BDXLCSfciBFixDA6poIDy7tryfcpglyw\nuq84ROrOBLU3kTaTM4zl8x2VRkGGdU88+7WhpVgB7s7uSJmzmWtojvDGp+1tylqp\nB4geNVB8rjqkZQjr9Y0oI2sJuIAYzDaBWwQsVUMmp2JO64kR8P1P7i99graUaGOd\nJwIDAQAB\n-----END PUBLIC KEY-----"

    #Oracle Object Storage
    region_name:str=os.getenv('REGION_NAME',"")
    aws_secret_access_key:str=os.getenv('AWS_SECRET_ACCESS_KEY',"")
    aws_access_key_id:str=os.getenv('AWS_ACCESS_KEY_ID',"")
    endpoint_url:str=os.getenv('ENDPOINT_URL',"")

    # Parameter

    ## Azure Config
    azure_b2c_openidconfiguration='https://seiryofesb2c.b2clogin.com/seiryofesb2c.onmicrosoft.com/v2.0/.well-known/openid-configuration?p=B2C_1_quaint-app'
    azure_b2c_audience='06b8cb1b-b866-43bf-9bc6-2898c6a149f3'
    azure_ad_openidconfiguration='https://login.microsoftonline.com/158e6d17-f3d5-4365-8428-26dfc74a9d27/v2.0/.well-known/openid-configuration'
    azure_ad_audience='0f2252c5-62ef-4aab-af65-99a753f1c77c'

    ## Azure AD groups UUID
    azure_ad_groups_quaint_admin='5c091517-25de-44bc-9e42-ffcb8539435c'
    azure_ad_groups_quaint_entry='63a40184-8dab-43b4-8367-54e84ace6e2a'
    azure_ad_groups_quaint_owner='a577d858-64bf-4815-aaf6-d893c654e92e'

    ## JWT EXPIRE
    access_token_expire:datetime.timedelta=datetime.timedelta(days=10)

    production_flag:int=os.getenv("PRODUCTION_FLAG",0)

    class Config:
        env_file = '../.env'
        secrets_dir='/run/secrets'

params=Parameters()
settings= Settings()
