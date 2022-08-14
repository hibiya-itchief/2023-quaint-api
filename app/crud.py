from curses import has_ic
from sqlalchemy.orm import Session
from fastapi import HTTPException, Query
from app import models,dep
from app.config import settings

#from hashids import Hashids
import ulid

from app import schemas



def get_user(db:Session,user_id:str):
    user = db.query(models.User).filter(models.User.id==user_id).first()
    if user:
        return user
    else:
        return None
    

def get_user_by_name(db:Session,username:str):
    user = db.query(models.User).filter(models.User.username==username).first()
    if user:
        return user
    else:
        return None

def get_all_users(db:Session):
    users = db.query(models.User).all()
    return users

def create_user(db:Session,user:schemas.UserCreate):
    hashed_password = dep.get_password_hash(user.password)
    db_user = models.User(id=ulid.new().str,username=user.username, is_family=False,is_active=False,password_expired=False,hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_by_admin(db:Session,user:schemas.UserCreateByAdmin):
    hashed_password = dep.get_password_hash(user.password)
    db_user = models.User(id=ulid.new().str,username=user.username,is_student=user.is_student, is_family=user.is_family,is_active=user.is_active,password_expired=user.password_expired,hashed_password=hashed_password)
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
    return db_user

def get_list_of_your_tickets(db:Session,user:schemas.User):
    db_tickets = db.query(models.Ticket).filter(models.Ticket.owner_id==user.id)
    return db_tickets

def create_group(db:Session,group:schemas.GroupCreate):
    db_group = models.Group(id=group.id,groupname=group.groupname,title=group.title,description=group.description,page_content=group.page_content,enable_vote=group.enable_vote,twitter_url=group.twitter_url,instagram_url=group.instagram_url,stream_url=group.stream_url)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group
def get_all_groups(db:Session):
    db_groups = db.query(models.Group).all()
    return db_groups
def get_group(db:Session,id:str):
    group = db.query(models.Group).filter(models.Group.id==id).first()
    if group:
        return group
    else:
        return None
def add_tag(db:Session,group_id:str,tag_input:schemas.GroupTagCreate):
    group = get_group(db,group_id)
    tag = get_tag(db,tag_input.tag_id)
    if not group:
        return None
    if not tag:
        return None
    db_grouptag = models.GroupTag(group_id=group.id,tag_id=tag.id)
    db.add(db_grouptag)
    db.commit()
    db.refresh(db_grouptag)
    return db_grouptag


def create_event(db:Session,group_id:str,event:schemas.EventCreate):
    group = get_group(db,group_id) 
    if not group:
        return None
    if not (event.sell_at<event.sell_ends and event.sell_ends<event.starts_at and event.starts_at<event.ends_at):
        return None
    db_event = models.Event(id=ulid.new().str,title=event.title,description=event.description,sell_at=event.sell_at,sell_ends=event.sell_ends,starts_at=event.starts_at,ends_at=event.ends_at,ticket_stock=event.ticket_stock,lottery=event.lottery,group_id=group_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_all_events(db:Session,group_id:str):
    db_events = db.query(models.Event).filter(models.Event.group_id==group_id).all()
    return db_events
def get_event(db:Session,group_id:str,event_id:str):
    db_event = db.query(models.Event).filter(models.Event.group_id==group_id,models.Event.id==event_id).first()
    if db_event:
        return db_event
    else:
        return None

## Ticket CRUD
def count_tickets_for_event(db:Session,event_id):
    db_tickets_count:int=db.query(models.Ticket).filter(models.Ticket.event_id==event_id).count()
    return db_tickets_count

def check_double_ticket(db:Session,event_id,user_id):
    db_already_taken:int = db.query(models.Ticket).filter(models.Ticket.event_id==event_id,models.Ticket.owner_id==user_id).count()
    if db_already_taken>0:
        return False
    else:
        return True
def create_ticket(db:Session,event_id,user_id,person):
    db_ticket = models.Ticket(id=ulid.new().str,event_id=event_id,owner_id=user_id,person=person)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


## Tag CRUD
def create_tag(db:Session,tag:schemas.TagCreate):
    db_tag=models.Tag(id=ulid.new(),tagname=tag.tagname)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag
def get_all_tags(db:Session):
    db_tags=db.query(models.Tag).all()
    return db_tags
def get_tag(db:Session,id:str):
    db_tag = db.query(models.Tag).filter(models.Tag.id==id).first()
    return db_tag
def put_tag(db:Session,id:str,tag:schemas.TagCreate):
    db_tag = db.query(models.Tag).filter(models.Tag.id==id).first()
    if not db_tag:
        return None
    db_tag.tagname=tag.tagname
    db.commit()
    db.refresh(db_tag)
    return db_tag
def delete_tag(db:Session,id:str):
    db_tag = db.query(models.Tag).filter(models.Tag.id==id).first()
    if not db_tag:
        return None
    db.delete(db_tag)
    db.commit()
    return 0




### 権限関係(Admin以外は要調整)

def grant_admin(db:Session,user:schemas.User):
    db_admin = models.Admin(user_id=user.id)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return "Grant Admin Successfully"

def grant_owner_of(db:Session,group:schemas.Group,user:schemas.User):
    db_owner = models.Authority(user_id=user.id,group_id=group.id,role=schemas.AuthorityRole.Owner)
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    return "Grant Owner Successfully"

def grant_authorizer_of(db:Session,group:schemas.Group,user:schemas.User):
    db_authorizer = models.Authority(user_id=user.id,group_id=group.id,role=schemas.AuthorityRole.Authorizer)
    db.add(db_authorizer)
    db.commit()
    db.refresh(db_authorizer)
    return "Grant Authorizer Successfully"

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

