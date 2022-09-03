from typing import List, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_
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
    user:schemas.User = db.query(models.User).filter(models.User.username==username).first()
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
    db_tickets:List[schemas.Ticket] = db.query(models.Ticket).filter(models.Ticket.owner_id==user.id).all()
    return db_tickets

def create_group(db:Session,group:schemas.GroupCreate):
    db_group = models.Group(id=group.id,groupname=group.groupname,title=group.title,description=group.description,page_content=group.page_content,enable_vote=group.enable_vote)
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
def update_title(db:Session,group:schemas.Group,title:Union[str,None]):
    db_group = db.query(models.Group).filter(models.Group.id==group.id).first()
    db_group.title=title
    db.commit()
    db.refresh(db_group)
    return db_group
def update_description(db:Session,group:schemas.Group,description:Union[str,None]):
    db_group = db.query(models.Group).filter(models.Group.id==group.id).first()
    db_group.description=description
    db.commit()
    db.refresh(db_group)
    return db_group
def update_twitter_url(db:Session,group:schemas.Group,twitter_url:Union[str,None]):
    db_group = db.query(models.Group).filter(models.Group.id==group.id).first()
    db_group.twitter_url=twitter_url
    db.commit()
    db.refresh(db_group)
    return db_group
def update_instagram_url(db:Session,group:schemas.Group,instagram_url:Union[str,None]):
    db_group = db.query(models.Group).filter(models.Group.id==group.id).first()
    db_group.instagram_url=instagram_url
    db.commit()
    db.refresh(db_group)
    return db_group
def update_stream_url(db:Session,group:schemas.Group,stream_url:Union[str,None]):
    db_group = db.query(models.Group).filter(models.Group.id==group.id).first()
    db_group.stream_url=stream_url
    db.commit()
    db.refresh(db_group)
    return db_group
def add_tag(db:Session,group_id:str,tag_id:schemas.GroupTagCreate):
    group = get_group(db,group_id)
    tag = get_tag(db,tag_id.tag_id)
    if not group:
        return None
    if not tag:
        return None
    try:
        db_grouptag = models.GroupTag(group_id=group.id,tag_id=tag.id)
        db.add(db_grouptag)
        db.commit()
        db.refresh(db_grouptag)
    except:
        raise HTTPException(200,"Already Registed")
    return db_grouptag
def get_tags_of_group(db:Session,group:schemas.Group):
    group = get_group(db,group.id)
    if not group:
        return None
    db_grouptags = db.query(models.GroupTag).filter(models.GroupTag.group_id==group.id).all()
    tags=[]
    for db_grouptag in db_grouptags:
        tags.append(db.query(models.Tag).filter(models.Tag.id==db_grouptag.tag_id).first())
    return tags

def update_thumbnail_image_url(db:Session,group:schemas.Group,image_url:str):
    db_group = db.query(models.Group).filter(models.Group.id==group.id).first()
    db_group.thumbnail_image_url = image_url
    db.commit()
    return db_group
def update_cover_image_url(db:Session,group:schemas.Group,image_url:str):
    db_group = db.query(models.Group).filter(models.Group.id==group.id).first()
    db_group.cover_image_url = image_url
    db.commit()
    return db_group

def delete_grouptag(db:Session,group:schemas.Group,tag:schemas.Tag):
    db.query(models.GroupTag).filter(models.GroupTag.group_id==group.id,models.GroupTag.tag_id==tag.id).delete()
    db.commit()
    return 0
def delete_group(db:Session,group:schemas.Group):
    db.query(models.Group).filter(models.Group.id==group.id).delete()
    db.commit()


def search_groups(db:Session,q:str):
    return db.query(models.Group).filter(or_(models.Group.groupname.contains(q),models.Group.title.contains(q),models.Group.description.contains(q))).all()


# Timetable
def create_timetable(db:Session,timetable:schemas.TimetableCreate):
    if not (timetable.sell_at<timetable.sell_ends and timetable.sell_ends<=timetable.starts_at and timetable.starts_at<timetable.ends_at):
        return None
    db_timetable = models.Timetable(id=ulid.new().str,timetablename=timetable.timetablename,sell_at=timetable.sell_at,sell_ends=timetable.sell_ends,starts_at=timetable.starts_at,ends_at=timetable.ends_at)
    db.add(db_timetable)
    db.commit()
    db.refresh(db_timetable)
    return db_timetable
def get_all_timetable(db:Session):
    return db.query(models.Timetable).all()
def get_timetable(db:Session,timetable_id:str):
    timetable:schemas.Timetable =  db.query(models.Timetable).filter(models.Timetable.id==timetable_id).first()
    return timetable
    

# Event
def create_event(db:Session,group_id:str,event:schemas.EventCreate):
    group = get_group(db,group_id) 
    if not group:
        return None
    if not get_timetable(db,event.timetable_id):
        return None
    # TODO Timetableに書き換え
    db_event = models.Event(id=ulid.new().str,timetable_id=event.timetable_id,ticket_stock=event.ticket_stock,lottery=event.lottery,group_id=group_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_all_events(db:Session,group_id:str):
    db_events = db.query(models.Event).filter(models.Event.group_id==group_id).all()
    return db_events
def get_event(db:Session,group_id:str,event_id:str):
    db_event:schemas.Event = db.query(models.Event).filter(models.Event.group_id==group_id,models.Event.id==event_id).first()
    if db_event:
        return db_event
    else:
        return None
def get_events_by_timetable(db:Session,timetable:schemas.Timetable):
    db_events:List[schemas.Event] = db.query(models.Event).filter(models.Event.timetable_id==timetable.id).all()
    return db_events

def delete_events(db:Session,event:schemas.Event):
    db.query(models.Event).filter(models.Event.id==event.id).delete()
    db.commit()

## Ticket CRUD
def count_tickets_for_event(db:Session,event:schemas.Event):
    db_tickets:List[schemas.Ticket]=db.query(models.Ticket).filter(models.Ticket.event_id==event.id).all()
    db_tickets_count:int = 0
    for ticket in db_tickets:
        db_tickets_count += ticket.person
    return db_tickets_count

def check_double_ticket(db:Session,event:schemas.Event,user:schemas.User):
    db_already_taken:int = 0
    ### このユーザーが同じ時間帯で他の公演のチケットを取っていないか(この公演の2枚目も含む)
    timetable = get_timetable(db,event.timetable_id)
    same_timetable_events = get_events_by_timetable(db,timetable)
    for same_timetable_event in same_timetable_events:
        db_already_taken += db.query(models.Ticket).filter(models.Ticket.event_id==same_timetable_event.id,models.Ticket.owner_id==user.id).count()
    if db_already_taken>0:
        return False
    else:
        return True
def create_ticket(db:Session,event:schemas.Event,user:schemas.User,person:int):
    db_ticket = models.Ticket(id=ulid.new().str,group_id=event.group_id,event_id=event.id,owner_id=user.id,person=person,is_used=False)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket
def get_ticket(db:Session,ticket_id):
    db_ticket:schemas.Ticket = db.query(models.Ticket).filter(models.Ticket.id==ticket_id).first()
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

def grant_entry(db:Session,user:schemas.User):
    db_entry = models.Entry(user_id=user.id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return "Grant Entry Successfully"

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

def check_entry(db:Session,user:schemas.User):
    if not db.query(models.Entry).filter(models.Entry.user_id==user.id).first():
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

def get_owner_list(db:Session,user:schemas.User):
    db_result = db.query(models.Authority).filter(models.Authority.user_id==user.id,models.Authority.role==schemas.AuthorityRole.Owner)
    owner_list = []
    for row in db_result:
        owner_list.append(row.group_id)
    return owner_list

def check_authorizer_of(db:Session,group:schemas.Group,user:schemas.User):
    if not db.query(models.Authority).filter(models.Authority.user_id==user.id,models.Authority.group_id==group.id,models.Authority.role==schemas.AuthorityRole.Authorizer).first():
        return False
    return True

def check_authorizer(db:Session,user:schemas.User):
    if not db.query(models.Authority).filter(models.Authority.user_id==user.id,models.Authority.role==schemas.AuthorityRole.Authorizer).first():
        return False
    return True

def get_authorizer_list(db:Session,user:schemas.User):
    db_result = db.query(models.Authority).filter(models.Authority.user_id==user.id,models.Authority.role==schemas.AuthorityRole.Authorizer)
    authorizer_list = []
    for row in db_result:
        authorizer_list.append(row.group_id)
    return authorizer_list
