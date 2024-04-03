from datetime import datetime, timedelta, timezone
from typing import Dict, List, Union

#from hashids import Hashids
import ulid
import pandas as pd
import numpy as np
from fastapi import HTTPException, Query
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, join
from sqlalchemy.sql import func

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
    groups_set=set()
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

def add_grouplink(db:Session,group_id:str,linktext:str,name:str):
    db_grouplink = models.GroupLink(id=ulid.new().str,group_id=group_id,linktext=linktext,name=name)
    db.add(db_grouplink)
    db.commit()
    db.refresh(db_grouplink)
    return db_grouplink
def get_grouplinks_of_group(db:Session,group:schemas.Group):
    db_grouplinks = db.query(models.GroupLink).filter(models.GroupLink.group_id==group.id).all()
    return db_grouplinks
def get_grouplink(db:Session,grouplink_id:str):
    db_grouplink = db.query(models.GroupLink).filter(models.GroupLink.id==grouplink_id).first()
    return db_grouplink
def delete_grouplink(db:Session,grouplink_id:str):
    db.query(models.GroupLink).filter(models.GroupLink.id==grouplink_id).delete()
    db.commit()
    return 0

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
    db_events:List[schemas.EventDBOutput] = db.query(models.Event).filter(models.Event.group_id==group_id).all()
    events:List[schemas.Event]=[]
    for e in db_events:
        event=schemas.Event(
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
        events.append(event)
    return events
def get_event(db:Session,event_id:str):
    e:schemas.EventDBOutput = db.query(models.Event).filter(models.Event.id==event_id).first()
    if e:
        event=schemas.Event(
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
        return event
    else:
        return None
def delete_events(db:Session,event:schemas.Event):
    db.query(models.Event).filter(models.Event.id==event.id).delete()
    db.commit()

## Ticket CRUD
def count_tickets_for_event(db:Session,event:schemas.Event)->int:
    res=db.query(func.sum(models.Ticket.person).label("person_sum")).filter(models.Ticket.event_id==event.id,or_(models.Ticket.status=="active",models.Ticket.status=="paper")).first()
    #db_tickets_count:int=db.query(models.Ticket).filter(models.Ticket.event_id==event.id,or_(models.Ticket.status=="active",models.Ticket.status=="paper")).count() #抽選機能を付けるのであれば、枚数確認せず抽選申し込みできるだろうという予想から、status!="cancelled"としなかった  紙整理券(paper)は含めた
    if res.person_sum is None:
        return 0
    return res.person_sum

def check_qualified_for_ticket(db:Session,event:schemas.Event,user:schemas.JWTUser):
    ### このユーザーが同じ時間帯で他の公演のチケットを取っていないか(この公演の2枚目も含む)
    ### 整理券の上限に達していないか(各公演の開始時刻で判定されます)
    taken_events:List[schemas.EventDBOutput] = db.query(models.Event) \
        .join(models.Ticket, \
        and_( models.Event.id==models.Ticket.event_id, \
            models.Ticket.owner_id==auth.user_object_id(user), \
            models.Ticket.status=="active" )) \
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
    db_ticket = models.Ticket(id=ulid.new().str,group_id=event.group_id,event_id=event.id,owner_id=auth.user_object_id(user),person=person,status="active",created_at=datetime.now(timezone(timedelta(hours=+9))).isoformat())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket
def spectest_ticket(db:Session,user:schemas.JWTUser):
    db_ticket = models.Ticket(id=ulid.new().str,group_id="testgroup",event_id="01H9PTVFH7CS30A5RKBKMAQ82R",owner_id=user.name,person=1,status="cancelled",created_at=datetime.now(timezone(timedelta(hours=+9))).isoformat())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket
def get_ticket(db:Session,ticket_id):
    db_ticket:schemas.Ticket = db.query(models.Ticket).filter(models.Ticket.id==ticket_id).first()
    return db_ticket
def delete_ticket(db:Session,ticket:schemas.Ticket):
    db_ticket=db.query(models.Ticket).filter(models.Ticket.id==ticket.id).first()
    db_ticket.status="cancelled"
    db.commit()
    db.refresh(db_ticket)
    return ticket
def use_ticket(db:Session,ticket_id:str):
    ticket=db.query(models.Ticket).filter(models.Ticket.id==ticket_id).first()
    if not ticket:
        return None
    ticket.status="used"
    db.commit()
    db.refresh(ticket)
    return ticket
def chief_create_ticket(db:Session,event:schemas.Event,user:schemas.JWTUser,person:int):
    db_ticket = models.Ticket(id=ulid.new().str,group_id=event.group_id,event_id=event.id,owner_id=user.name,person=person,status="paper",created_at=datetime.now(timezone(timedelta(hours=+9))).isoformat())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket
def chief_delete_ticket(db:Session,event:schemas.Event):
    db_ticket=db.query(models.Ticket).filter(models.Ticket.event_id==event.id,models.Ticket.status=="paper").first()
    if db_ticket is None:
        return None
    db_ticket.status="cancelled"
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


# Vote CRUD
def create_vote(db:Session,group_id1:str,group_id2:str,user:schemas.JWTUser):
    try:
        db_vote=models.Vote(user_id=auth.user_object_id(user),group_id_21=group_id2,group_id_11=group_id1)
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
    #本当はここ学年しばりしたい
    db_votes1:List[schemas.Vote]=db.query(models.Vote).filter(models.Vote.group_id_21==group.id).count()
    # db_votes2:List[schemas.Vote]=db.query(models.Vote).filter(models.Vote.group_id_22==group.id).all()
    # db_votes3:List[schemas.Vote]=db.query(models.Vote).filter(models.Vote.group_id_23==group.id).all()
    db_votes4:List[schemas.Vote]=db.query(models.Vote).filter(models.Vote.group_id_11==group.id).count()
    # db_votes5:List[schemas.Vote]=db.query(models.Vote).filter(models.Vote.group_id_12==group.id).all()
    # db_votes6:List[schemas.Vote]=db.query(models.Vote).filter(models.Vote.group_id_13==group.id).all()
    return (db_votes1 + db_votes4)

def get_hebe_nowplaying(db:Session):
    return db.query(models.HebeNowplaying).first()
def get_hebe_upnext(db:Session):
    return db.query(models.HebeUpnext).first()
def set_hebe_nowplaying(db:Session,hebe:schemas.HebeResponse):
    db_hebe:schemas.HebeResponse=db.query(models.HebeNowplaying).first()
    if db_hebe is None:
        add_hebe=models.HebeNowplaying(group_id=hebe.group_id)
        db.add(add_hebe)
        db.commit()
        db.refresh(add_hebe)
        return add_hebe
    db_hebe.group_id=hebe.group_id
    db.commit()
    db.refresh(db_hebe)
    return db_hebe
def set_hebe_upnext(db:Session,hebe:schemas.HebeResponse):
    db_hebe:schemas.HebeResponse=db.query(models.HebeUpnext).first()
    if db_hebe is None:
        add_hebe=models.HebeUpnext(group_id=hebe.group_id)
        db.add(add_hebe)
        db.commit()
        db.refresh(add_hebe)
        return add_hebe
    db_hebe.group_id=hebe.group_id
    db.commit()
    db.refresh(db_hebe)
    return db_hebe

#受け取ったpandas.DataFrameをserializeする
#受け取った値についての検証はcolumnsだけ行う
def convert_df(df:pd.DataFrame) -> pd.DataFrame:
    #カラムの数が正しいかの検証
    if len(df.columns.values) != 12:
        raise HTTPException(422, f'列の数が合いません。正しい列の数は12です。サンプルシートと比較して確認してください。')

    converted_df = pd.DataFrame(columns=['group_id', 'eventname', 'lottery', 'target', 'ticket_stock', 'starts_at', 'ends_at', 'sell_starts', 'sell_ends'])

    #1行ずつ取り出してserializeする
    for i in range(len(df)):
        try:
            #時間の情報をserializeする
            year = str(df.iat[i, 5])
            month = str(df.iat[i, 6])
            day = str(df.iat[i, 7])
            hours = {
                'starts_at':str(df.iat[i, 8]).split(':')[0],
                'ends_at':str(df.iat[i, 9]).split(':')[0],
                'sell_starts':str(df.iat[i, 10]).split(':')[0],
                'sell_ends':str(df.iat[i, 11]).split(':')[0],
            }

            """
            month, day, hourのserialize
            上の三つを時間にくっつける上で 9 → 09 みたいにする必要がある
            """
            if len(month) == 1:
                month = '0' + month
            if len(day) == 1:
                day = '0' + day

            for key in ['starts_at', 'ends_at', 'sell_starts', 'sell_ends']:
                if len(hours[key]) == 1:
                    hours[key] = '0' + hours[key]

            times = {
                'starts_at':hours['starts_at'] + ':' + str(df.iat[i , 8]).split(':')[1] + ':' + str(df.iat[i , 8]).split(':')[2],
                'ends_at':hours['ends_at'] + ':' + str(df.iat[i , 9]).split(':')[1] + ':' + str(df.iat[i , 9]).split(':')[2],
                'sell_starts':hours['sell_starts'] + ':' + str(df.iat[i , 10]).split(':')[1] + ':' + str(df.iat[i , 10]).split(':')[2],
                'sell_ends':hours['sell_ends'] + ':' + str(df.iat[i , 11]).split(':')[1] + ':' + str(df.iat[i , 11]).split(':')[2],
            }

            converted_df = pd.concat([converted_df, pd.DataFrame(data={
                'group_id':[df.iat[i , 0]],
                'eventname':[df.iat[i , 1]],
                'lottery':df.iat[i , 2],
                'target':[df.iat[i , 3]],
                'ticket_stock':[df.iat[i , 4]],
                'starts_at':[ year + '-' + month + '-' + day + 'T' + times['starts_at'] + '+09:00'],
                'ends_at':[ year + '-' + month + '-' + day + 'T' + times['ends_at'] + '+09:00'],
                'sell_starts':[ year + '-' + month + '-' + day + 'T' + times['sell_starts'] + '+09:00'],
                'sell_ends':[ year + '-' + month + '-' + day + 'T' + times['sell_ends'] + '+09:00'],
            })], ignore_index=True)
        except:
            raise HTTPException(422, f"pandas.DataFrameの変換に失敗しました。表記方法が正しいことを確認してください。<エラー箇所> 行番号 : { i + 1 }")

    return converted_df

#受け取ったpandas.DataFrameの形式が正しいかを検証する
def check_df(db:Session, df: pd.DataFrame) -> None:
    #カラム名が正しいかの検証
    columns = df.columns.values
    correct_columns = ['group_id', 'eventname', 'lottery', 'target', 'ticket_stock', 'starts_at', 'ends_at', 'sell_starts', 'sell_ends']
    for i in range(len(columns)):
        if not (columns[i] == correct_columns[i]):
            raise HTTPException(422, f'カラム名が正しいことを確認してください。<エラー箇所> 表記 : {columns[i]}, 正表記 : {correct_columns[i]}')

    #group_idが正しいかの検証
    for i in range(len(df)):
        group = db.query(models.Group).filter(models.Group.id == df.iat[i, 0]).first()

        if not group:
            raise HTTPException(400, f"存在しないgroup_idが含まれています。<エラー箇所> 行番号 : {i + 1}, group_id : {df.iat[i, 0]}")
        
    #時刻の表記の仕方が正しいかの判定
    for m in range(len(df)):
        for n in [5,6,7,8]:
            try:
                time = datetime.fromisoformat(df.iat[m, n])
            except:
                raise HTTPException(422, f"時刻の表記方法が正しいことを確認してください。<エラー箇所> 行番号 : {m + 1}, 列番号 : {n + 1}")
            
    #時刻の設定に問題がないかを確認
    for i in range(len(df)):
        starts_at = datetime.fromisoformat(df.iat[i , 5])
        ends_at = datetime.fromisoformat(df.iat[i , 6])
        sell_starts = datetime.fromisoformat(df.iat[i , 7])
        sell_ends = datetime.fromisoformat(df.iat[i , 8])

        if starts_at > ends_at:
            raise HTTPException(400,f"公演の開始時刻は終了時刻よりも前である必要があります。group_id : {df.iat[i , 0]}, eventname : {df.iat[i , 1]}")
        if sell_starts > sell_ends:
            raise HTTPException(400,f"配布開始時刻は配布終了時刻よりも前である必要があります。group_id : {df.iat[i , 0]}, eventname : {df.iat[i , 1]}")

    #表記方法に問題なし
    return None

#pandas.DataFrameの情報を元にDBにeventを追加
def create_events_from_df(db:Session, df: pd.DataFrame) -> None:
    for i in range(len(df)):
        group_id = df.iat[i , 0]

        #pandas.DataFrameの情報を読み取ってスキーマに変換
        event = schemas.EventDBInput(
            eventname=df.iat[i , 1],
            lottery=df.iat[i , 2],
            target=df.iat[i , 3],
            ticket_stock=df.iat[i , 4],
            starts_at=df.iat[i , 5],
            ends_at=df.iat[i , 6],
            sell_starts=df.iat[i , 7],
            sell_ends=df.iat[i , 8],
        )

        db_event = models.Event(id=ulid.new().str,group_id=group_id,**event.dict())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

    return None