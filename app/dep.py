from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from yarg import get
from sqlalchemy.orm.session import Session

from .database import SessionLocal,engine
from . import schemas,crud

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context= CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db:Session, username: str, password: str):
    user= crud.get_user_by_name(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def login_for_access_token(username:str,password:str,db:Session):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=10)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(db:Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user:schemas.User = crud.get_user_by_name(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    if user.password_expired:
        raise HTTPException(401,detail="Password expired")
    return user


def admin(db:Session = Depends(get_db),user:schemas.User = Depends(get_current_user)):
    if not crud.check_admin(db,user):
        raise HTTPException(403,detail="Permittion Error")
    return user

def owner_of(groupname:str,db:Session = Depends(get_db),user:schemas.User = Depends(get_current_user)):
    group=crud.get_group_by_name(db,groupname)
    if not group:
        raise HTTPException(400,detail='Group "'+groupname+'" does not exist')
    if crud.check_admin(db,user):
        return user
    if not crud.check_owner_of(db,group,user):
        raise HTTPException(403,detail="Permittion Error")
    return user

def owner(db:Session = Depends(get_db),user:schemas.User = Depends(get_current_user)):
    if crud.check_admin(db,user):
        return user
    if not crud.check_owner(db,user):
        raise HTTPException(403,detail="Permittion Error")
    return user

def authorizer_of(groupname:str,db:Session = Depends(get_db),user:schemas.User=Depends(get_current_user)):
    group=crud.get_group_by_name(db,groupname)
    if not group:
        raise HTTPException(400,detail='Group "'+groupname+'" does not exist')
    if crud.check_admin(db,user):
        return user
    if crud.check_owner_of(db,group,user):
        return user
    if not crud.check_authorizer_of(db,group,user):
        raise HTTPException(403,detail="Permittion Error")
    return user

def authorizer(db:Session = Depends(get_db),user:schemas.User=Depends(get_current_user)):
    if crud.check_admin(db,user):
        return user
    if crud.check_owner(db,user):
        return user
    if not crud.check_authorizer(db,user):
        raise HTTPException(403,detail="Permittion Error")
    return user

