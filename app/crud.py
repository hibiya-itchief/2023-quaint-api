from curses import has_ic
from sqlalchemy.orm import Session
from fastapi import Query
from app import models,dep
from app.config import settings

from hashids import Hashids

from app import schemas

hashids = Hashids(salt=settings.HASHIDS_SALT,min_length=7)

def get_user(db:Session,user_id:int):
    id=int(hashids.decode(user_id)[0])
    user = db.query(models.User).filter(models.User.id==id).first()
    if user:
        user_result = models.User(id=hashids.encode(user.id),username=user.username,hashed_password=user.hashed_password,is_student=user.is_student,is_family=user.is_family,is_active=user.is_active,password_expired=user.password_expired)
        return user_result
    else:
        return None
    

def get_user_by_name(db:Session,username:str):
    user = db.query(models.User).filter(models.User.username==username).first()
    if user:
        user_result = models.User(id=hashids.encode(user.id),username=user.username,hashed_password=user.hashed_password,is_student=user.is_student,is_family=user.is_family,is_active=user.is_active,password_expired=user.password_expired)
        return user_result
    else:
        return None

def get_all_users(db:Session):
    raw_users = db.query(models.User).all()
    users=[]
    for user in raw_users:
        user.id = hashids.encode(user.id)
        users.append(user)
    return users

def get_group(db:Session,group_id:str):
    id=int(hashids.decode(group_id)[0])
    group = db.query(models.Group).filter(models.Group.id==id).first()
    if group:
        group_result = models.Group(id=hashids.encode(group.id),groupname=group.groupname,title=group.title,description=group.description,page_content=group.page_content,enable_vote=group.enable_vote)
        return group_result
    else:
        return None

'''
def get_group_by_name(db:Session,groupname:str):
    group = db.query(models.Group).filter(models.Group.groupname==groupname).first()
    if group:
        group_result = models.Group(id=hashids.encode(group.id),groupname=group.groupname,title=group.title,description=group.description)
        return group_result
    else:
        return None
        '''

def create_user(db:Session,user:schemas.UserCreate):
    hashed_password = dep.get_password_hash(user.password)
    db_user = models.User(username=user.username, is_family=False,is_active=False,password_expired=False,hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_by_admin(db:Session,user:schemas.UserCreateByAdmin):
    hashed_password = dep.get_password_hash(user.password)
    db_user = models.User(username=user.username, is_family=user.is_family,is_active=user.is_active,password_expired=user.password_expired,hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def change_password(db:Session,user:schemas.PasswordChange):
    db_user=db.query(models.User).filter(models.User.username==user.username).first()
    hashed_new_password = dep.get_password_hash(user.new_password)
    db_user.hashed_password=hashed_new_password
    db_user.password_expired=False
    db.commit()
    return user

## Tag CRUD
def create_tag(db:Session,tag:schemas.TagCreate):
    db_tag=models.Tag(tagname=tag.tagname)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    tag = models.Tag(id=hashids.encode(db_tag.id),tagname=db_tag.tagname,groups=db_tag.groups)
    return tag
def get_all_tags(db:Session):
    db_tags=db.query(models.Tag).all()
    tags=[]
    for tag in db_tags:
        tag.id = hashids.encode(tag.id)
        tags.append(tag)
    return tags
def get_tag(db:Session,hashids_id:str):
    try:
        id=int(hashids.decode(hashids_id)[0])
        db_tag = db.query(models.Tag).filter(models.Tag.id==id).first()
    except:
        return None
    if db_tag:
        tag = models.Tag(id=hashids.encode(db_tag.id),tagname=db_tag.tagname,groups=db_tag.groups)
        return tag
    return None
def put_tag(db:Session,hashids_id:str,tag:schemas.TagCreate):
    try:
        id=int(hashids.decode(hashids_id)[0])
        db_tag = db.query(models.Tag).filter(models.Tag.id==id).first()
    except:
        return None
    db_tag.tagname=tag.tagname
    db.commit()
    db.refresh(db_tag)
    tag_result = models.Tag(id=hashids.encode(db_tag.id),tagname=db_tag.tagname,groups=db_tag.groups)
    return tag_result
def delete_tag(db:Session,hashids_id:str):
    try:
        id=int(hashids.decode(hashids_id)[0])
        db_tag = db.query(models.Tag).filter(models.Tag.id==id).first()
    except:
        return None
    db.delete(db_tag)
    db.commit()
    return 0




### 権限関係(Admin以外は要調整)

def grant_admin(db:Session,user:schemas.User):
    id = int(hashids.decode(user.id)[0])
    db_admin = models.Admin(user_id=id)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def grant_owner_of(db:Session,group:schemas.Group,user:schemas.User):
    db_owner = models.Authority(user_id=user.id,group_id=group.id,role=schemas.AuthorityRole.Owner)
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    return db_owner

def grant_authorizer_of(db:Session,group:schemas.Group,user:schemas.User):
    db_authorizer = models.Authority(user_id=user.id,group_id=group.id,role=schemas.AuthorityRole.Authorizer)
    db.add(db_authorizer)
    db.commit()
    db.refresh(db_authorizer)
    return db_authorizer

def check_admin(db:Session,user:schemas.User):
    id = int(hashids.decode(user.id)[0])
    if not db.query(models.Admin).filter(models.Admin.user_id==id).first():
        return False
    return True

def check_owner_of(db:Session,group:schemas.Group,user:schemas.User):
    id = int(hashids.decode(user.id)[0])
    if not db.query(models.Authority).filter(models.Authority.user_id==id,models.Authority.group_id==group.id,models.Authority.role==schemas.AuthorityRole.Owner).first():
        return False
    return True

def check_owner(db:Session,user:schemas.User):
    if not db.query(models.Authority).filter(models.Authority.user_id==user.id,models.Authority.role==schemas.AuthorityRole.Owner).first():
        return False
    return True

def check_authorizer_of(db:Session,group:schemas.Group,user:schemas.User):
    if not db.query(models.Authority).filter(models.Authority.user_id==user.id,models.Authority.group_id==group.id,models.Authority.role==schemas.AuthorityRole.Authorizer).first():
        return False
    return True

def check_authorizer(db:Session,user:schemas.User):
    if not db.query(models.Authority).filter(models.Authority.user_id==user.id,models.Authority.role==schemas.AuthorityRole.Authorizer).first():
        return False
    return True

