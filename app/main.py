from datetime import datetime,timedelta
from typing import Optional,List,Union

from fastapi import FastAPI,Depends,HTTPException,status,Query
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import SessionLocal, engine

from . import dep,schemas,models,crud


#models.Base.metadata.create_all(bind=engine)

description="""
日比谷高校オンライン整理券システム「QUAINT」のAPI
"""
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs."
        
    },
]

app = FastAPI(title="QUAINT-API",description=description,openapi_tags=tags_metadata)



@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(db:Session = Depends(dep.get_db),form_data: OAuth2PasswordRequestForm = Depends()):
    return dep.login_for_access_token(form_data.username,form_data.password,db)


@app.get("/users/",response_model=List[schemas.User],tags=["users"],description="Required Authority: **Admin**")
def read_all_users(permittion:schemas.User = Depends(dep.admin),db:Session=Depends(dep.get_db)):
    users = crud.get_all_users(db)
    return users

@app.post("/users",response_model=schemas.Token,tags=["users"])
def create_user(user:schemas.UserCreate,db:Session=Depends(dep.get_db)):
    db_user = crud.get_user_by_name(db,username=user.username)
    if db_user:
        raise HTTPException(status_code=400,detail="username already registered")
    crud.create_user(db=db,user=user)
    return dep.login_for_access_token(user.username,user.password,db)

@app.put("/users/me/password",tags=["users"])
def change_password(user:schemas.PasswordChange,db:Session=Depends(dep.get_db)):
    if not dep.authenticate_user(db,user.username,user.password):
        raise HTTPException(401,"Incorrect Username or Password")
    crud.change_password(db,user)
    return HTTPException(200,"Password changed successfully")

@app.put("/users/{user_id}/authority",tags=["users"])
def grant_authority(user_id:int,role:schemas.AuthorityRole,group_id:Union[int,None]=None,permittion:schemas.User=Depends(dep.admin),db:Session=Depends(dep.get_db)):
    user=crud.get_user(db,user_id)
    if not user:
        raise HTTPException(404,"User Not Found")

    if role ==schemas.AuthorityRole.Admin:
        if crud.check_admin(db,user):
            raise HTTPException(200)
        return crud.grant_admin(db,user)
    else:
        if not group_id:
            raise HTTPException(400,"Invalid Parameter")
        group = crud.get_group(db,group_id)
        if not group:
            raise HTTPException(404,"Group Not Found")
        if role == schemas.AuthorityRole.Owner:
            if crud.check_owner_of(db,group,user):
                raise HTTPException(200)
            return crud.grant_owner_of(db,group,user)
        elif role == schemas.AuthorityRole.Authorizer:
            if crud.check_authorizer_of(db,group,user):
                raise HTTPException(200)
            return crud.grant_authorizer_of(db,group,user)
    
    

@app.post("/admin/users",response_model=schemas.User,tags=["admin"],description="Required Authority: **Admin**")
def create_user_by_admin(user:schemas.UserCreateByAdmin,permittion:schemas.User = Depends(dep.admin),db:Session=Depends(dep.get_db)):
    db_user = crud.get_user_by_name(db,username=user.username)
    if db_user:
        raise HTTPException(status_code=400,detail="username already registered")
    return crud.create_user(db=db,user=user)



#@app.put("/admin/user")