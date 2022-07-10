from datetime import datetime,timedelta
from typing import Optional,List,Union

from fastapi import FastAPI,Depends,HTTPException,status,Query
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas


from .database import SessionLocal, engine

from . import dep,models,crud


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
        "name":"groups",
        "description":"groups that has events"
    },
    {
        "name": "tags",
        "description": "Tags for Group"
        
    },

]

app = FastAPI(title="QUAINT-API",description=description,openapi_tags=tags_metadata)




@app.get("/")
def read_root():
    return {
        "title": "QUAINT-API",
        "description":"日比谷高校オンライン整理券システム「QUAINT」のAPI"
    }

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(db:Session = Depends(dep.get_db),form_data: OAuth2PasswordRequestForm = Depends()):
    return dep.login_for_access_token(form_data.username,form_data.password,db)

@app.post("/users",response_model=schemas.Token,tags=["users"])
def create_user(user:schemas.UserCreate,db:Session=Depends(dep.get_db)):
    db_user = crud.get_user_by_name(db,username=user.username)
    if db_user:
        raise HTTPException(status_code=400,detail="username already registered")
    crud.create_user(db=db,user=user)
    return dep.login_for_access_token(user.username,user.password,db)
@app.get("/users",response_model=List[schemas.User],tags=["users"],description="Required Authority: **Admin**")
def read_all_users(permittion:schemas.User = Depends(dep.admin),db:Session=Depends(dep.get_db)):
    users = crud.get_all_users(db)
    return users
@app.put("/users/me/password",tags=["users"])
def change_password(user:schemas.PasswordChange,db:Session=Depends(dep.get_db)):
    if not dep.authenticate_user(db,user.username,user.password):
        raise HTTPException(401,"Incorrect Username or Password")
    if user.password==user.new_password:
        raise HTTPException(400,"Enter different password from present")
    crud.change_password(db,user)
    return HTTPException(200,"Password changed successfully")
'''
@app.put("/users/{user_id}/authority",tags=["users"])
def grant_authority(user_id:int,role:schemas.AuthorityRole,group_id:Union[int,None]=None,permittion:schemas.user.User=Depends(dep.admin),db:Session=Depends(dep.get_db)):
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
'''



@app.post("/groups",response_model=schemas.Group,tags=["groups"],description="Required Authority: **Admin**")
def create_group(group:schemas.GroupCreate,permission:schemas.User=Depends(dep.admin),db:Session=Depends(dep.get_db)):
    return crud.create_group(db,group)
@app.get("/groups",response_model=List[schemas.GroupMin],tags=["groups"])
def get_all_groups(db:Session=Depends(dep.get_db)):
    return crud.get_all_groups(db)
@app.get("/groups/{group_id}",response_model=schemas.Group,tags=["groups"])
def get_group(group_id:str,db:Session=Depends(dep.get_db)):
    group_result = crud.get_group(db,group_id)
    if not group_result:
        raise HTTPException(404,"Group Not Found")
    return group_result


@app.post("/tags",response_model=schemas.Tag,tags=["tags"])
def create_tag(tag:schemas.TagCreate,permittion:schemas.User = Depends(dep.admin),db:Session=Depends(dep.get_db)):
    return crud.create_tag(db,tag)
@app.get("/tags",response_model=List[schemas.Tag],tags=["tags"])
def get_all_tags(db:Session=Depends(dep.get_db)):
    return crud.get_all_tags(db)
@app.get("/tags/{tag_id}",response_model=schemas.Tag,tags=["tags"])
def get_tag(tag_id:str,db:Session = Depends(dep.get_db)):
    tag_result = crud.get_tag(db,tag_id)
    if not tag_result:
        raise HTTPException(404,"Tag Not Found")
    return tag_result
@app.put("/tags/{tag_id}",response_model=schemas.Tag,tags=["tags"])
def change_tag_name(tag_id:str,tag:schemas.TagCreate,permittion:schemas.User=Depends(dep.admin),db:Session = Depends(dep.get_db)):
    tag_result = crud.put_tag(db,tag_id,tag)
    if not tag_result:
        raise HTTPException(404,"Tag Not Found")
    return tag_result
@app.delete("/tags/{tag_id}",tags=["tags"])
def delete_tag(tag_id:str,permittion:schemas.User=Depends(dep.admin),db:Session = Depends(dep.get_db)):
    result = crud.delete_tag(db,tag_id)
    if result==None:
        raise HTTPException(404,"Tag Not Found")
    return "Successfully Deleted"
    

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