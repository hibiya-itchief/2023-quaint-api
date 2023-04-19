from datetime import datetime, timedelta
from typing import Any, Dict, Union

import jwt
import requests
from fastapi import Depends, HTTPException
from fastapi.openapi.models import HTTPBearer
from fastapi.security.base import SecurityBase
from jwt import PyJWKClient
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app import schemas
from app.config import settings

B2C_CONFIG=requests.get(settings.azure_b2c_openidconfiguration).json()
AD_CONFIG=requests.get(settings.azure_ad_openidconfiguration).json()
b2c_jwks_client = PyJWKClient(B2C_CONFIG['jwks_uri'])
ad_jwks_client = PyJWKClient(AD_CONFIG['jwks_uri'])

class BearerAuth(SecurityBase):
    def __init__(
        self
    ):
        self.model = HTTPBearer(description="")
        self.scheme_name = "Azure AD・B2C"
        self.auto_error=True

    async def __call__(self, request: Request) -> str:
        try:
            authorization: str = request.headers.get("Authorization")
            authorization=authorization.split(' ')[-1] # Authorization header sometimes includes space like 'Bearer token..'
            if not authorization:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="ログインが必要です"
                )
            return authorization
        except:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="不正なトークンです"
            )
auth_scheme=BearerAuth()

def verify_jwt(token:str=Depends(auth_scheme))->Dict[str,Any]:
    try:
        header=jwt.get_unverified_header(token)
        payload=jwt.decode(token,options={"verify_signature": False})
        if payload.get("iss")==B2C_CONFIG['issuer']:
            signing_key = b2c_jwks_client.get_signing_key_from_jwt(token)
            decoded_jwt = jwt.decode(token, signing_key.key, algorithms=header['alg'],audience=settings.azure_b2c_audience)
            return decoded_jwt
        elif payload.get("iss")==AD_CONFIG['issuer']:
            signing_key = ad_jwks_client.get_signing_key_from_jwt(token)
            decoded_jwt = jwt.decode(token, signing_key.key, algorithms=header['alg'],audience=settings.azure_ad_audience)
            return decoded_jwt
        else:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,detail="不正なトークンです")
    except Exception as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,detail=f"不正なトークンです( {e} )")

def get_current_user(decoded_jwt:Dict = Depends(verify_jwt))->schemas.JWTUser:
    user = schemas.JWTUser(**decoded_jwt)
    return user

def user_object_id(user:schemas.JWTUser):
    if user.iss == B2C_CONFIG['issuer']:
        return user.sub
    elif user.iss == AD_CONFIG['issuer']:
        if user.oid is not None:
            return user.oid
    raise Exception("User Object IDがありません")

#例外を発生させないことで、ログインしてるならユーザー情報が取れるし、してないならNoneを返すようにする(顔出し画像が入る可能性があるカバー画像をレスポンスするか決める)
def get_current_user_not_exception():
    try:
        user=verify_jwt()
        return user
    except:
        return None

### Role
def check_school(user:schemas.JWTUser):
    try:
        if user.iss==AD_CONFIG['issuer']:
            return True
        else:
            return False
    except:
        return False
def school(user:schemas.JWTUser=Depends(get_current_user)):
    if check_school(user):
        return user
    else:
        raise HTTPException(HTTP_403_FORBIDDEN,detail="本校生徒・学校関係者である必要があります")

def check_visited(user:schemas.JWTUser):
    try:
        if user.iss==AD_CONFIG['issuer'] or (user.jobTitle and ('Visited' in user.jobTitle or 'visited' in user.jobTitle)):
            return True
        else:
            return False
    except:
        return False
def visited(user:schemas.JWTUser=Depends(get_current_user)):
    if check_visited(user):
        return user
    else:
        raise HTTPException(HTTP_403_FORBIDDEN,detail="入校処理がされていません")

def check_admin(user:schemas.JWTUser):
    try:
        if user.groups and settings.azure_ad_groups_quaint_admin in user.groups:
            return True
        else:
            return False
    except:
        return False
def admin(user:schemas.JWTUser = Depends(get_current_user)):
    if check_admin(user):
        return user
    else:
        raise HTTPException(HTTP_403_FORBIDDEN,detail="admin(管理者)の権限がありません")

def check_entry(user:schemas.JWTUser):
    try:
        if (user.groups and settings.azure_ad_groups_quaint_entry in user.groups) or check_admin(user):
            return True
        else:
            return False
    except:
        return False
def entry(user:schemas.JWTUser = Depends(get_current_user)):
    if check_entry(user): # entry or admin
        return user
    else:
        raise HTTPException(HTTP_403_FORBIDDEN,detail="entry(入校処理担当者)の権限がありません")

def check_owner(user:schemas.JWTUser):
    try:
        if (user.groups and settings.azure_ad_groups_quaint_owner in user.groups) or check_admin(user):
            return True
        else:
            return False
    except:
        return False
def owner(user:schemas.JWTUser = Depends(get_current_user)):
    if  check_owner(user): # owner or admin
        return user
    else:
        raise HTTPException(HTTP_403_FORBIDDEN,detail="Owner(クラ代・団体代表者)の権限がありません")

    


