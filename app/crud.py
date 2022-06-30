from sqlalchemy.orm import Session

from app import models,schemas

def get_user(db:Session,user_id:int):
    return db.query(models.User).filter(models.User.id==user_id).first()

def get_user_by_name(db:Session,username:str):
    return db.query(models.User).filter(models.User.username==username).first()

def get_all_users(db:Session):
    return db.query(models.User).all()


def create_user(db:Session,user:schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(username=user.username, is_family=user.is_family,is_active=user.is_active,password_expired=user.password_expired,hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user