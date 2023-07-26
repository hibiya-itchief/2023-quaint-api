from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set, Union

#from hashids import Hashids
import ulid
from fastapi import HTTPException, Query
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, join

from app import auth, models, schemas, storage
from app.config import params, settings


def time_overlap(start1:datetime,end1:datetime,start2:datetime,end2:datetime)->bool:
    #境界は含まない
    if(start2<end1 and start1<end2): # 重なってる
        return True
    else:
        return False

def grant_ownership(db:Session,group:schemas.Group,user_oid:str,note:Union[str,None])->schemas.GroupOwner:
    db_groupowner=models.GroupOwner(group_id=group.id,user_id=user_oid,note=note)
    db.add(db_groupowner)
    db.commit()
    db.refresh(db_groupowner)
    return db_groupowner

def delete_ownership(db:Session,group_id:str,user_oid:str)->int:
    db.query(models.GroupOwner).filter(models.GroupOwner.group_id==group_id, models.GroupOwner.user_id==user_oid).delete()
    db.commit()
    return 0
def get_all_ownership(db:Session)->List[schemas.GroupOwner]:
    db_gos=db.query(models.GroupOwner).all()
    return db_gos
def get_ownership_of_user(db:Session,user_oid:str)->List[str]:
    db_gos:List[schemas.GroupOwner]=db.query(models.GroupOwner).filter(models.GroupOwner.user_id==user_oid).all()
    result:List[str]=[]
    for row in db_gos:
        result.append(row.group_id)
    return result
def check_owner_of(db:Session,user:schemas.JWTUser,group_id:str):
    try:
        if group_id in get_ownership_of_user(db,auth.user_object_id(user)):
            return True
        else:
            return False
    except:
        return False

def get_list_of_your_tickets(db:Session,user:schemas.JWTUser):
    db_tickets:List[schemas.Ticket] = db.query(models.Ticket).filter(models.Ticket.owner_id==auth.user_object_id(user)).all()
    return db_tickets

def create_readauthority(db:Session,readauthority:schemas.ReadAuthorityCreate):
    db_readauthority = models.ReadAuthority(id=ulid.new(),**readauthority.dict())
    db.add(db_readauthority)
    db.commit()
    db.refresh(db_readauthority)
    return db_readauthority
def get_readauthority(db:Session,id:str)->schemas.ReadAuthority:
    db_readauthority = db.query(models.ReadAuthority).filter(models.ReadAuthority.id==id).first()
    return db_readauthority
def get_all_readauthority(db:Session)->List[schemas.ReadAuthority]:
    db_readauthoritys = db.query(models.ReadAuthority).all()
    return db_readauthoritys

def create_group(db:Session,group:schemas.GroupCreate):
    db_group = models.Group(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def get_all_groups_public(db:Session)->List[schemas.Group]:
    query = db.query(models.Group , models.Tag) \
            .select_from(models.Group)\
            .outerjoin(models.GroupTag , models.GroupTag.group_id==models.Group.id) \
            .outerjoin(models.Tag , models.Tag.id==models.GroupTag.tag_id).all()
    tags_of_each_group:Dict[str,List[schemas.Tag]]=dict()
    groups_set:Set[schemas.Group]=set()
    for q in query:
        group:schemas.Group=q.Group
        groups_set.add(group)
        if tags_of_each_group.get(group.id) is None:
            tags_of_each_group[group.id]=[]
        if q.Tag:
            tags_of_each_group[group.id].append(q.Tag)
    groups=[]
    for g in groups_set:
        g.tags=tags_of_each_group[g.id]
        groups.append(g)
    # ここループ2回回すの改善したい 2重ループじゃないからまあ耐えなのか
    return groups

def get_group_public(db:Session,id:str)->Union[schemas.Group,None]:
    query = db.query(models.Group , models.Tag) \
            .select_from(models.Group).filter(models.Group.id==id) \
            .outerjoin(models.GroupTag , models.GroupTag.group_id==models.Group.id)\
            .outerjoin(models.Tag , models.Tag.id==models.GroupTag.tag_id).all()
    if query:
        group:schemas.Group=query[0].Group
        tags:List[schemas.Tag]=[]
        for q in query:
            if q.Tag is not None:
                tags.append(q.Tag)
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

def change_public_thumbnail_image_url(db:Session,group:schemas.Group,public_thumbnail_image_url:Union[str,None])->schemas.Group:
    db_group:models.Group = db.query(models.Group).filter(models.Group.id==group.id).first()
    db_group.public_thumbnail_image_url=public_thumbnail_image_url
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
    add_event:schemas.EventDBInput=event
    add_event.starts_at=event.starts_at.isoformat()
    add_event.ends_at=event.ends_at.isoformat()
    add_event.sell_starts=event.sell_starts.isoformat()
    add_event.sell_ends=event.sell_ends.isoformat()
    db_event = models.Event(id=ulid.new().str,group_id=group_id,**add_event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
def get_all_events(db:Session,group_id:str):
    query = db.query(models.Event,models.ReadAuthority) \
            .select_from(models.Event).filter(models.Event.group_id==group_id) \
            .outerjoin(models.EventReadAuthority , models.EventReadAuthority.event_id==models.Event.id) \
            .outerjoin(models.ReadAuthority , models.ReadAuthority.id==models.EventReadAuthority.readauthority_id).all()
    readauthorities_of_each_event:Dict[str,List[schemas.ReadAuthority]]=dict()
    events_set:Set[schemas.Event]=set()
    for q in query:
        event=schemas.Event(
            id=q.Event.id,
            group_id=q.Event.group_id,
            eventname=q.Event.eventname,
            lottery=q.Event.lottery,
            target=q.Event.target,
            ticket_stock=q.Event.ticket_stock,
            starts_at=datetime.fromisoformat(q.Event.starts_at),
            ends_at=datetime.fromisoformat(q.Event.ends_at),
            sell_starts=datetime.fromisoformat(q.Event.sell_starts),
            sell_ends=datetime.fromisoformat(q.Event.sell_ends),
        )
        events_set.add(event)
        if readauthorities_of_each_event.get(event.id) is None:
            readauthorities_of_each_event[event.id]=[]
        if q.ReadAuthority:
            readauthorities_of_each_event[event.id].append(q.ReadAuthority)
    events:List[schemas.Event]=[]
    for event in events_set:
        event.readauthority=readauthorities_of_each_event[event.id]
        events.append(event)
    return events
def get_event(db:Session,event_id:str):
    query = db.query(models.Event,models.ReadAuthority) \
            .select_from(models.Event).filter(models.Event.id==event_id) \
            .outerjoin(models.EventReadAuthority , models.EventReadAuthority.event_id==models.Event.id) \
            .outerjoin(models.ReadAuthority , models.ReadAuthority.id==models.EventReadAuthority.readauthority_id).all()
    if query:
        event=schemas.Event(
            id=query[0].Event.id,
            group_id=query[0].Event.group_id,
            eventname=query[0].Event.eventname,
            lottery=query[0].Event.lottery,
            target=query[0].Event.target,
            ticket_stock=query[0].Event.ticket_stock,
            starts_at=datetime.fromisoformat(query[0].Event.starts_at),
            ends_at=datetime.fromisoformat(query[0].Event.ends_at),
            sell_starts=datetime.fromisoformat(query[0].Event.sell_starts),
            sell_ends=datetime.fromisoformat(query[0].Event.sell_ends),
        )
        readauthorities:List[schemas.ReadAuthority]=[]
        for q in query:
            if q.ReadAuthority:
                readauthorities.append(q.ReadAuthority)
        event.readauthority=readauthorities
        return event
    else:
        return None
def add_readauthority_to_event(db:Session,event:schemas.Event,readauthority:schemas.ReadAuthority):
    db_event_readauthority = models.EventReadAuthority(event_id=event.id,readauthority_id=readauthority.id)
    db.add(db_event_readauthority)
    db.commit()
    db.refresh(db_event_readauthority)
    return db_event_readauthority
def delete_readauthority_from_event(db:Session,event:schemas.Event,readauthority:schemas.ReadAuthority):
    db.query(models.EventReadAuthority).filter(models.EventReadAuthority.event_id==event.id,models.EventReadAuthority.readauthority_id==readauthority.id).delete()
    db.commit()
    return 0
def delete_events(db:Session,event:schemas.Event):
    db.query(models.Event).filter(models.Event.id==event.id).delete()
    db.commit()

## Ticket CRUD
def count_tickets_for_event(db:Session,event:schemas.Event):
    db_tickets_count:int=db.query(models.Ticket).filter(models.Ticket.event_id==event.id).count()
    return db_tickets_count

def check_qualified_for_ticket(db:Session,event:schemas.Event,user:schemas.JWTUser):
    ### このユーザーが同じ時間帯で他の公演のチケットを取っていないか(この公演の2枚目も含む)
    ### 整理券の上限に達していないか(各公演の開始時刻で判定されます)
    taken_events:List[schemas.EventDBOutput] = db.query(models.Event) \
        .join(models.Ticket, \
        and_( models.Event.id==models.Ticket.event_id, \
            models.Ticket.owner_id==auth.user_object_id(user) )) \
        .all()
    tickets_num_per_day:int=0
    for taken_event in taken_events:
        e=taken_event
        te=schemas.Event(
            id=e.id,
            group_id=e.group_id,
            eventname=e.eventname,
            lottery=e.lottery,
            target=e.target,
            ticket_stock=e.ticket_stock,
            starts_at=datetime.fromisoformat(e.starts_at),
            ends_at=datetime.fromisoformat(e.ends_at),
            sell_starts=datetime.fromisoformat(e.sell_starts),
            sell_ends=datetime.fromisoformat(e.sell_ends),
        )
        if(time_overlap(te.starts_at,te.ends_at,event.starts_at,event.ends_at)):
            return False
        if(params.max_tickets_per_day!=0 and event.starts_at.date()==te.starts_at.date()): # 1人1日何枚まで の制限がある かつ 二つのEventの日付部分が等しいなら
            tickets_num_per_day+=1
    
    if(params.max_tickets!=0 and len(taken_events)>params.max_tickets): # 1人何枚まで の制限がある かつ それをオーバーしている
        return False
    if(params.max_tickets_per_day!=0 and tickets_num_per_day+1>params.max_tickets_per_day): # 1人1日何枚までの制限がある かつ それをオーバーしている
        return False
    return True
def create_ticket(db:Session,event:schemas.Event,user:schemas.JWTUser,person:int):
    db_ticket = models.Ticket(id=ulid.new().str,group_id=event.group_id,event_id=event.id,owner_id=auth.user_object_id(user),person=person,is_used=False,created_at=datetime.now(timezone(timedelta(hours=+9))).isoformat())
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


# Vote
def create_vote(db:Session,group_id:str,user:schemas.JWTUser):
    try:
        db_vote=models.Vote(group_id=group_id,user_id=auth.user_object_id(user))
        db.add(db_vote)
        db.commit()
        db.refresh(db_vote)
        return db_vote
    except IntegrityError as e:
        raise HTTPException(400,"投票は1人1回までです")

def get_user_vote(db:Session,user:schemas.JWTUser):
    db_vote:schemas.Vote=db.query(models.Vote).filter(models.Vote.user_id==auth.user_object_id(user)).first()
    return db_vote
def get_group_votes(db:Session,group:schemas.Group):
    db_votes:List[schemas.Vote]=db.query(models.Vote).filter(models.Vote.group_id==group.id).all()
    return db_votes




