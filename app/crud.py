from datetime import datetime
from typing import List, Union

#from hashids import Hashids
import ulid
from fastapi import HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import auth, models, schemas, storage
from app.config import params, settings


def time_overlap(start1:datetime,end1:datetime,start2:datetime,end2:datetime)->bool:
    #境界は含まない
    if(start2<end1 and start1<end2): # 重なってる
        return True
    else:
        return False

def grant_ownership(db:Session,group:schemas.Group,user_sub:str)->schemas.GroupOwner:
    db_groupowner=models.GroupOwner(group_id=group.id,user_id=user_sub)
    db.add(db_groupowner)
    db.commit()
    db.refresh(db_groupowner)
    return db_groupowner

def delete_ownership(db:Session,group_id:str,user_sub:str)->schemas.GroupOwner:
    try:
        db.query(models.GroupOwner).filter(models.GroupOwner.group_id==group_id, models.GroupOwner.user_id==user_sub).delete()
        db.commit()
        return 0
    except:
        return None
def get_all_ownership(db:Session)->List[schemas.GroupOwner]:
    db_gos=db.query(models.GroupOwner).all()
    return db_gos
def get_ownership_of_user(db:Session,user_sub:str)->List[str]:
    db_gos:List[schemas.GroupOwner]=db.query(models.GroupOwner).filter(models.GroupOwner.user_id==user_sub).all()
    result:List[str]=[]
    for row in db_gos:
        result.append(row.group_id)
    return result
def check_owner_of(db:Session,user:schemas.JWTUser,group_id:str):
    try:
        if group_id in get_ownership_of_user(db,user.sub):
            return True
        else:
            return False
    except:
        return False

def get_list_of_your_tickets(db:Session,user:schemas.JWTUser):
    db_tickets:List[schemas.Ticket] = db.query(models.Ticket).filter(models.Ticket.owner_id==user.id).all()
    return db_tickets

def create_group(db:Session,group:schemas.GroupCreate):
    db_group = models.Group(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group
def get_all_groups_public(db:Session)->List[schemas.Group]:
    db_groups:List[schemas.Group] = db.query(models.Group).all()
    for db_group in db_groups:
        db_grouptags = db.query(models.GroupTag).filter(models.GroupTag.group_id==db_group.id).all()
        tags:List[schemas.Tag]=[]
        for db_grouptag in db_grouptags:
            tags.append(db.query(models.Tag).filter(models.Tag.id==db_grouptag.tag_id).first())
        db_group.tags=tags
    return db_groups
def get_group_public(db:Session,id:str)->schemas.Group:
    group:schemas.Group = db.query(models.Group).filter(models.Group.id==id).first()
    if group:
        db_grouptags = db.query(models.GroupTag).filter(models.GroupTag.group_id==group.id).all()
        tags:List[schemas.Tag]=[]
        for db_grouptag in db_grouptags:
            tags.append(db.query(models.Tag).filter(models.Tag.id==db_grouptag.tag_id).first())
        group.tags=tags
        return group
    else:
        return None

def update_group(db:Session,group:schemas.Group,updated_group:schemas.GroupUpdate):
    db_group:models.Group = db.query(models.Group).filter(models.Group.id==group.id).first()
    db_group.update_dict(updated_group.dict())
    db.commit()
    db.refresh(db_group)
    return db_group

def add_tag(db:Session,group_id:str,tag_id:schemas.GroupTagCreate):
    group = get_group_public(db,group_id)
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
    group = get_group_public(db,group.id)
    if not group:
        return None
    db_grouptags = db.query(models.GroupTag).filter(models.GroupTag.group_id==group.id).all()
    tags=[]
    for db_grouptag in db_grouptags:
        tags.append(db.query(models.Tag).filter(models.Tag.id==db_grouptag.tag_id).first())
    return tags

def delete_grouptag(db:Session,group:schemas.Group,tag:schemas.Tag):
    db.query(models.GroupTag).filter(models.GroupTag.group_id==group.id,models.GroupTag.tag_id==tag.id).delete()
    db.commit()
    return 0
def delete_group(db:Session,group:schemas.Group):
    db.query(models.Group).filter(models.Group.id==group.id).delete()
    db.commit()

# Event
def create_event(db:Session,group_id:str,event:schemas.EventCreate):
    db_event = models.Event(id=ulid.new().str,group_id=group_id,**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
def get_all_events(db:Session,group_id:str):
    db_events:List[schemas.Event] = db.query(models.Event).filter(models.Event.group_id==group_id).all()
    return db_events
def get_event(db:Session,group_id:str,event_id:str):
    db_event:schemas.Event = db.query(models.Event).filter(models.Event.id==event_id).first()
    if db_event:
        return db_event
    else:
        return None
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

def check_qualified_for_ticket(db:Session,event:schemas.Event,user:schemas.JWTUser):
    ### このユーザーが同じ時間帯で他の公演のチケットを取っていないか(この公演の2枚目も含む)
    ### 整理券の上限に達していないか(各公演の開始時刻で判定されます)
    taken_tickets:List[schemas.Ticket] = db.query(models.Ticket).filter(models.Ticket.owner_id==user.id).all()
    tickets_num_per_day:int=0
    for taken_ticket in taken_tickets:
        te=get_event(db,taken_ticket.event_id)
        if(time_overlap(te.starts_at,te.ends_at,event.starts_at,event.ends_at)):
            return False
        if(params.max_tickets_per_day!=0 and event.starts_at.date()==te.starts_at.date()):
            tickets_num_per_day+=1
    
    if(params.max_tickets!=0 and len(taken_tickets)>params.max_tickets):
        return False
    if(params.max_tickets_per_day!=0 and tickets_num_per_day+1>params.max_tickets_per_day):
        return False
    
    return True
def create_ticket(db:Session,event:schemas.Event,user:schemas.JWTUser,person:int):
    db_ticket = models.Ticket(id=ulid.new().str,group_id=event.group_id,event_id=event.id,owner_id=user.sub,person=person,is_used=False)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket
def get_ticket(db:Session,ticket_id):
    db_ticket:schemas.Ticket = db.query(models.Ticket).filter(models.Ticket.id==ticket_id).first()
    return db_ticket
def delete_ticket(db:Session,ticket:schemas.Ticket):
    db.query(models.Ticket).filter(models.Ticket.id==ticket.id).delete()
    db.commit()


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




