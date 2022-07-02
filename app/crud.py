from sqlalchemy.orm import Session
from fastapi import Query
from app import models,schemas,dep

def get_user(db:Session,user_id:int):
    return db.query(models.User).filter(models.User.id==user_id).first()

def get_user_by_name(db:Session,username:str):
    return db.query(models.User).filter(models.User.username==username).first()

def get_all_users(db:Session):
    return db.query(models.User).all()

def get_group(db:Session,group_id:int):
    return db.query(models.Group).filter(models.Group.id==group_id).first()

def get_group_by_name(db:Session,groupname:str):
    return db.query(models.Group).filter(models.Group.groupname==groupname).first()

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


def grant_admin(db:Session,user:schemas.User):
    db_admin = models.Admin(user_id=user.id)
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
    if not db.query(models.Admin).filter(models.Admin.user_id==user.id).first():
        return False
    return True

def check_owner_of(db:Session,group:schemas.Group,user:schemas.User):
    if not db.query(models.Authority).filter(models.Authority.user_id==user.id,models.Authority.group_id==group.id,models.Authority.role==schemas.AuthorityRole.Owner).first():
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

