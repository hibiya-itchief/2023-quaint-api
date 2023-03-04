from datetime import datetime, timedelta
from typing import Union

import jwt
import requests
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.openapi.models import HTTPBearer
from fastapi.security.base import SecurityBase
from jwt import PyJWKClient
from sqlalchemy.orm.session import Session
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app import schemas
from app.config import settings

from .database import SessionLocal,engine
from . import crud

B2C_CONFIG=requests.get(settings.azure_b2c_openidconfiguration).json()
AD_CONFIG=requests.get(settings.azure_ad_openidconfiguration).json()
b2c_jwks_client = PyJWKClient(B2C_CONFIG['jwks_uri'])
ad_jwks_client = PyJWKClient(AD_CONFIG['jwks_uri'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BearerAuth(SecurityBase):
    def __init__(
        self
    ):
        self.model = HTTPBearer(description="")
        self.scheme_name = "Azure AD・B2C"
        self.auto_error=True

    async def __call__(self, request: Request) -> str:
        authorization: str = request.headers.get("Authorization")
        authorization=authorization.split(' ')[-1] # Authorization header sometimes includes space like 'Bearer token..'
        if not authorization:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="ログインが必要です"
            )
        return authorization
auth_scheme=BearerAuth()

def generate_jwt(data:Dict,expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if data.get("aud") is None:
        to_encode.update({"aud": "quaint"})
    if data.get("iss") is None:
        to_encode.update({"iss": "https://api.seiryofes.com"})
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,settings.jwt_privatekey,algorithm="RS256")
    return encoded_jwt

def verify_jwt(token:str=Depends(auth_scheme))->schemas.JWTUser:
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
        elif payload.get("iss")=="https://api.seiryofes.com/admin/access_token":
            decoded_jwt = jwt.decode(token,settings.jwt_publickey,algorithms=['RS256'],audience="quaint")
            return decoded_jwt
        else:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,detail="不正なトークンです")
    except Exception as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,detail=f"不正なトークンです( {e} )")

def get_current_user(user:schemas.JWTUser = Depends(verify_jwt)):
    return user


#例外を発生させないことで、ログインしてるならユーザー情報が取れるし、してないならNoneを返すようにする(顔出し画像が入る可能性があるカバー画像をレスポンスするか決める)
def get_current_user_not_exception():
    try:
        user=verify_jwt()
        return user
    except:
        return None

### Role

def school(user:schemas.JWTUser=Depends(get_current_user)):
    if user.iss==AD_CONFIG['issuer']:
        return 

def visited(user:schemas.JWTUser=Depends(get_current_user)):
    if user.iss==AD_CONFIG['issuer'] or (user.jobTitle and ('Visited' in user.jobTitle or 'visited' in user.jobTitle)):
        return user
    else:
        raise HTTPException(HTTP_403_FORBIDDEN,detail="入校処理がされていません")

def admin(user:schemas.JWTUser = Depends(get_current_user)):
    if user.groups and settings.azure_ad_groups_quaint_admin in user.groups:
        return user
    else:
        raise HTTPException(HTTP_403_FORBIDDEN,detail="admin(quaintの管理者)の権限がありません")

def entry(user:schemas.JWTUser = Depends(get_current_user)):
    if user.groups and (settings.azure_ad_groups_quaint_entry in user.groups or settings.azure_ad_groups_quaint_admin in user.groups): # entry or admin
        return user
    else:
        raise HTTPException(HTTP_403_FORBIDDEN,detail="entry(入校処理担当者)の権限がありません")

def owner(user:schemas.JWTUser = Depends(get_current_user)):
    if user.groups and (settings.azure_ad_groups_quaint_owner in user.groups or settings.azure_ad_groups_quaint_admin in user.groups):
        return user
    else:
        raise HTTPException(HTTP_403_FORBIDDEN,detail="Owner(団体代表者)の権限がありません")
