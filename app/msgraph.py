import json
import time
from typing import Union

import jwt
import requests

from app.config import settings


class MsGraph:
    _access_token:str
    def __init__(self) -> None:
        self._access_token=self.get_access_token()
    def get_access_token(self) -> str:
        if(settings.b2c_msgraph_secret is None):
            raise Exception("missing msgraph_secret")
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        payload = {
            'client_id': settings.b2c_msgraph_client,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials',
            'client_secret': settings.b2c_msgraph_secret
        }

        TokenGet_URL = "https://login.microsoftonline.com/" + \
            settings.b2c_msgraph_tenant + "/oauth2/v2.0/token"

        response = requests.get(
            TokenGet_URL,
            headers=headers,
            data=payload
        )
        # requrest処理のクローズ
        response.close
        # その結果を取得
        jsonObj = json.loads(response.text)
        return jsonObj["access_token"]
    def access_token(self)->str:
        payload=jwt.decode(self._access_token,options={"verify_signature": False})
        if payload.get("exp")<time.time():
            self._access_token=self.get_access_token()
        return self._access_token

    def change_jobTitle(self,user_sub:str,jobTitle:str)->Union[bool,requests.Response]:
        headers = {
            'Authorization': 'Bearer ' + self.access_token(),
            'Content-Type': 'application/json'
        }
        url="https://graph.microsoft.com/v1.0/users/"+user_sub
        payload={
            'jobTitle': jobTitle
        }
        response=requests.patch(
            url=url,
            headers=headers,
            json=payload
        )
        return response
        
    


