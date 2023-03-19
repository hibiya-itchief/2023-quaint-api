import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union
from xml.dom.minidom import Entity

from fastapi import (Body, Depends, FastAPI, File, HTTPException, Query,
                     UploadFile, status)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import Field
from sqlalchemy.orm import Session
from starlette.status import (HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
                              HTTP_404_NOT_FOUND)

from app import auth, crud, db, models, schemas, storage
from app.config import settings
from app.msgraph import MsGraph

#models.Base.metadata.create_all(bind=engine)

description="""
日比谷高校オンライン整理券システム「QUAINT」のAPI \n
<a href="https://seiryofes.com">seiryofes.com</a>
<a href="https://github.com/hibiya-itchief/quaint-api">GitHub</a> \n \n
"""
if settings.production_flag==1:
    description+="<h2>本番環境</h2>"

tags_metadata = [
    {
        "name": "users",
        "description": "ユーザー",
    },
    {
        "name":"groups",
        "description":"Group : 星陵祭に参加する各団体"
    },
    {
        "name":"events",
        "description":"Event : 各参加団体がもつ公演"
    },
    {
        "name":"tickets",
        "description":"Ticket : 各公演に入場するための整理券"
    },
    {
        "name": "tags",
        "description": "Tag : Groupにひもづけられるタグ"
    },

]

app = FastAPI(title="QUAINT-API",description=description,openapi_tags=tags_metadata,version="0.1.0")
### TODO 同一オリジンにアップロードしてcorsは許可しない
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

msgraph=MsGraph()

@app.get("/")
def read_root():
    return {
        "title": "QUAINT-API",
        "description":"日比谷高校オンライン整理券システム「QUAINT」のAPI"
    }

@app.get(
    "/users/me/tickets",
    response_model=List[schemas.Ticket],
    summary="ログイン中のユーザーが所有している整理券のリストを取得",
    tags=["users"],
    description="### 必要な権限\nなし\n### ログインが必要か\nはい")
def get_list_of_your_tickets(user:schemas.JWTUser = Depends(auth.get_current_user),db:Session=Depends(db.get_db)):
    return crud.get_list_of_your_tickets(db,user)

@app.put(
    "/users/{user_sub}/visit",
    summary="ユーザーの入校処理",
    tags=["users"],
    description="### 必要な権限\nEntry\n### ログインが必要か\nはい\n")
def activate_user(user_sub:str,permission:schemas.JWTUser=Depends(auth.entry),db:Session=Depends(db.get_db)):
    result=msgraph.change_jobTitle(user_sub,jobTitle="Visited")
    if result.status_code==204:
        return {"OK":True}
    raise HTTPException(result.status_code,result.text)

@app.get(
    "/users/me/owner_of",
    response_model=List[str],
    summary="ownerが自分が権限のある団体を確認する",
    tags=["users"],
    description="### 必要な権限\nowner\n### ログインが必要か\nはい\n")
def check_ownership_of_user(user:schemas.JWTUser=Depends(auth.owner),db:Session=Depends(db.get_db)):
    return crud.get_ownership_of_user(db,user.sub)
@app.get(
    "/users/{user_sub}/owner_of",
    response_model=List[str],
    summary="ユーザーの権限のある団体を確認する",
    tags=["users"],
    description="### 必要な権限\nadmin\n### ログインが必要か\nはい\n")
def check_ownership_of_user(user_sub:str,permission:schemas.JWTUser=Depends(auth.admin),db:Session=Depends(db.get_db)):
    return crud.get_ownership_of_user(db,user_sub)
@app.get(
    "/users/owner_of",
    response_model=List[str],
    summary="団体代表者のユーザーと団体の紐づけを全て確認する",
    tags=["users"],
    description="### 必要な権限\nadmin\n### ログインが必要か\nはい\n")
def check_all_ownership(permission:schemas.JWTUser=Depends(auth.admin),db:Session=Depends(db.get_db)):
    return crud.get_all_ownership(db)
@app.put(
    "/users/{user_sub}/owner_of",
    response_model=schemas.GroupOwner,
    summary="団体代表者のユーザーとGroupを紐づける",
    tags=["users"],
    description="### 必要な権限\nadmin\n### ログインが必要か\nはい\n")
def grant_ownership(user_sub:str,group_id:str,permission=Depends(auth.admin),db:Session=Depends(db.get_db)):
    group=crud.get_group_public(db,group_id)
    if not group:
        raise HTTPException(404,"グループが見つかりません")
    return crud.grant_ownership(db,group,user_sub)
@app.delete(
    "/users/{user_sub}/owner_of",
    summary="団体代表者のユーザーとGroupの紐づけを削除",
    tags=["users"],
    description="### 必要な権限\nadmin\n### ログインが必要か\nはい\n")
def delete_ownership(user_sub:str,group_id:str,permission=Depends(auth.admin),db:Session=Depends(db.get_db)):
    result=crud.delete_ownership(db,group_id,user_sub)
    if not result:
        raise HTTPException(404,"グループまたはユーザーが見つかりません")
    return {"OK":True}


@app.post(
    "/groups",
    response_model=List[schemas.Group],
    summary="新規Groupの作成",
    tags=["groups"],
    description='### 必要な権限\nAdmin\n### ログインが必要か\nはい\n### 説明\n- オブジェクトではなく配列の形でjsonを渡してください\n- 複数のGroupの一括作成ができます\n- 各種URLを指定せずに作成する場合は、"twitter_url":""のように空文字ではなくパラメータ自体をjsonに記述せずNoneにしてください',)
def create_group(groups:List[schemas.GroupCreate],permission:schemas.JWTUser=Depends(auth.admin),db:Session=Depends(db.get_db)):
    result=[]
    for group in groups:
        result.append(crud.create_group(db,group))
    return result
@app.get(
    "/groups",
    response_model=List[schemas.Group],
    summary="全Groupの情報を取得",
    tags=["groups"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ")
def get_all_groups(db:Session=Depends(db.get_db)):
    return crud.get_all_groups_public(db)
@app.get(
    "/groups/{group_id}",
    response_model=schemas.Group,
    summary="指定されたGroupの情報を取得",
    tags=["groups"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ",
    responses={"404":{"description":"指定されたGroupが見つかりません"}})
def get_group(group_id:str,db:Session=Depends(db.get_db)):
    group_result = crud.get_group_public(db,group_id)
    if not group_result:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    return group_result

@app.get("/groups/{group_id}/private")
def get_group_private():
    pass

@app.put(
    "/groups/{group_id}",
    summary="Groupを更新",
    tags=['groups'],
    description="### 必要な権限\nAdminまたは当該グループのOwner\n### ログインが必要か\nはい",
    responses={"404":{"description":"指定されたGroupまたはTagが見つかりません"}})
def update_group(group_id:str,updated_group:schemas.GroupUpdate,db:Session=Depends(db.get_db)):
    group=crud.get_group_public(db,group_id)
    u=crud.update_group(db,group,updated_group)
    return u

@app.put(
    "/groups/{group_id}/tags",
    summary="指定されたGroupにタグを紐づける",
    tags=["groups"],
    description="### 必要な権限\nAdminまたは当該グループのOwner\n### ログインが必要か\nはい",
    responses={"404":{"description":"指定されたGroupまたはTagが見つかりません"}})
def add_tag(group_id:str,tag_id:schemas.GroupTagCreate,user:schemas.JWTUser=Depends(auth.get_current_user),db:Session=Depends(db.get_db)):
    group = crud.get_group_public(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    if not(auth.check_admin(user) or crud.check_owner_of(db,user,group.id)):
        raise HTTPException(401,"Adminまたは当該GroupのOwnerの権限が必要です")
    grouptag = crud.add_tag(db,group_id,tag_id)
    if not grouptag:
        raise HTTPException(404,"Tagが見つかりません")
    tag=crud.get_tag(db,tag_id.tag_id)
    return "Add Tag Successfully"
@app.delete(
    "/groups/{group_id}/tags/{tag_id}",
    summary="指定されたGroupに紐づいている指定されたTagを削除",
    tags=["groups"],
    description="### 必要な権限\nAdminまたは当該グループのOwner\n### ログインが必要か\nはい\n",
    responses={"404":{"description":"- 指定されたGroupが見つかりません\n- 指定されたTagが見つかりません"}})
def delete_grouptag(group_id:str,tag_id:str,user:schemas.JWTUser=Depends(auth.get_current_user),db:Session=Depends(db.get_db)):
    group = crud.get_group_public(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    if not(crud.check_admin(db,user) or crud.check_owner_of(db,group,user)):
        raise HTTPException(401,"Adminまたは当該GroupのOwnerの権限が必要です")
    tag = crud.get_tag(db,tag_id)
    if not tag:
        raise HTTPException(404,"指定されたTagが見つかりません")
    tag=crud.get_tag(db,tag_id)
    return crud.delete_grouptag(db,group,tag)
@app.delete(
    "/groups/{group_id}",
    summary="指定されたGroupを削除",
    tags=["groups"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい\n### 説明\n指定するGroupに紐づけられているEvent,Ticket,Tagをすべて削除しないと削除できません",
    responses={"404":{"description":"指定されたGroupが見つかりません"},
        "400":{"description":"指定されたGroupに紐づけられているEvent,Ticket,Tagをすべて削除しないと削除できません"}})
def delete_group(group_id:str,permission:schemas.JWTUser=Depends(auth.admin),db:Session=Depends(db.get_db)):
    group = crud.get_group_public(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    try:
        crud.delete_group(db,group)
        return {"OK":True}
    except:
        raise HTTPException(400,"指定されたGroupに紐づけられているEvent,Ticket,Tagをすべて削除しないと削除できません")


### Event Crud
@app.post(
    "/groups/{group_id}/events",
    response_model=schemas.Event,
    summary="新規Eventを作成",
    tags=["events"],
    description="### 必要な権限\nadmin\n### ログインが必要か\nはい\n### 説明\n- 公演を作成します。",
    responses={"400":{"description":"パラメーターが不適切です"},
        "403":{"description":"Adminの権限が必要です"},
        "404":{"description":"指定されたGroupが見つかりません"}})
def create_event(group_id:str,event:schemas.EventCreate,user:schemas.JWTUser=Depends(auth.admin),db:Session=Depends(db.get_db)):
    group = crud.get_group_public(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    if event.starts_at > event.ends_at:
        raise HTTPException(400,"公演の開始時刻は終了時刻よりも前である必要があります")
    if event.sell_starts > event.sell_ends:
        raise HTTPException(400,"配布開始時刻は配布終了時刻よりも前である必要があります")
    existed_events=crud.get_all_events(db,group.id)
    for ee in existed_events:
        if event.starts_at < ee.ends_at and ee.starts_at < event.ends_at:
            raise HTTPException(400,"ひとつの団体が同一時間帯で2つ以上の公演を作ることはできません")
    result = crud.create_event(db,group_id,event)
    if not result:
        raise HTTPException(400,"パラメーターが不適切です")
    return result
@app.get(
    "/groups/{group_id}/events",
    response_model=List[schemas.Event],
    summary="指定されたGroupの全Eventを取得",
    tags=["events"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n")
def get_all_events(group_id:str,db:Session=Depends(db.get_db)):
    return crud.get_all_events(db,group_id)
@app.get(
    "/groups/{group_id}/events/{event_id}",
    response_model=schemas.Event,
    summary="指定されたGroupの指定されたEevntを取得",
    tags=["events"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n",
    responses={"404":{"description":"指定されたGroupまたはEventが見つかりません"}})
def get_event(group_id:str,event_id:str,db:Session=Depends(db.get_db)):
    event = crud.get_event(db,event_id)
    if not event:
        raise HTTPException(404,"指定されたGroupまたはEventが見つかりません")
    return event
@app.delete(
    "/groups/{group_id}/events/{event_id}",
    summary="指定されたGroupの指定されたEventを削除",
    tags=["events"],
    description="### 必要な権限\nadmin\n### ログインが必要か\nはい\n### 説明\n指定するEventに紐づけられたTicketを全て削除しないと削除できません",
    responses={"404":{"description":"指定されたGroupまたはEventがありません"},
        "403":{"description":"Adminの権限が必要です"},
        "400":{"description":"指定されたEventに紐づけられたTicketを全て削除しないと削除できません"}})
def delete_events(group_id:str,event_id:str,user:schemas.JWTUser=Depends(auth.admin),db:Session=Depends(db.get_db)):
    event = crud.get_event(db,event_id)
    if not event:
        raise HTTPException(404,"指定されたGroupまたはEventがありません")
    group = crud.get_group_public(db,event.group_id)
    try:
        crud.delete_events(db,event)
        return {"OK":True}
    except:
        raise HTTPException(400,"指定されたEventに紐づけられたTicketを全て削除しないと削除できません")

### Ticket CRUD


@app.post(
    "/groups/{group_id}/events/{event_id}/tickets",
    response_model=schemas.Ticket,
    summary="整理券取得",
    tags=["tickets"],
    description="### 必要な権限\nアクティブ(校内に来場済み)なユーザーであること\n### ログインが必要か\nはい\n### 説明\n整理券取得できる条件\n- ユーザーが校内に来場ずみ\n- 現在時刻が取りたい整理券の配布時間内\n- 当該公演の整理券在庫が余っている\n- ユーザーは既にこの整理券を取得していない\n- ユーザーは既に当該公演と同じ時間帯の公演の整理券を取得していない\n- 同時入場人数は生徒用アカウントは1名まで、それ以外は3名まで",
    responses={"404":{"description":"- 指定されたGroupまたはEventが見つかりません\n- 既にこの公演・この公演と同じ時間帯の公演の整理券を取得している場合、新たに取得はできません\n- この公演の整理券は売り切れています\n- 現在整理券の配布時間外です"},
        "400":{"description":"- 同時入場人数は3人まで(本校生徒は1人)までです\n- 校内への来場処理をしたユーザーのみが整理券を取得できます"}})
def create_ticket(group_id:str,event_id:str,person:int,user:schemas.JWTUser=Depends(auth.get_current_user),db:Session=Depends(db.get_db)):
    event = crud.get_event(db,event_id)
    if not event:
        raise HTTPException(404,"指定されたGroupまたはEventが見つかりません")
    if not (event.target==schemas.EventTarget.guest or (event.target==schemas.EventTarget.visited and auth.check_visited(user)) or (event.target==schemas.EventTarget.school and auth.check_school(user))):
        raise HTTPException(HTTP_403_FORBIDDEN,str(event.target)+"ユーザーのみが整理券を取得できます。校内への入場処理が済んでいるか確認してください。")
    if event.sell_starts<datetime.now(timezone(timedelta(hours=+9))) and datetime.now(timezone(timedelta(hours=+9)))<event.sell_ends:
        if crud.count_tickets_for_event(db,event)+person<=event.ticket_stock and crud.check_qualified_for_ticket(db,event,user):##まだチケットが余っていて、同時間帯の公演の整理券取得ではない
            if auth.check_school(user)==False and 0<person<4:#一般アカウント(家族アカウント含む)は1アカウントにつき3人まで入れる
                return crud.create_ticket(db,event,user,person)
            elif auth.check_school(user) and person==1:
                return crud.create_ticket(db,event,user,person)
            else:
                raise HTTPException(400,"同時入場人数は3人まで(本校生徒は1人)までです")
        elif not crud.check_qualified_for_ticket(db,event,user):
            raise HTTPException(404,"既にこの公演・この公演と重複する時間帯の公演の整理券を取得している場合、新たに取得はできません。または取得できる整理券の枚数の上限を超えています")
        else:
            raise HTTPException(404,"この公演の整理券は売り切れています")
    else:
        raise HTTPException(404,"現在整理券の配布時間外です")

@app.get(
    "/groups/{group_id}/events/{event_id}/tickets",
    response_model=schemas.TicketsNumberData,
    summary="指定された公演の整理券の枚数情報を取得",
    tags=["tickets"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n",
    responses={"404":{"description":"- 指定されたGroupが見つかりません\n- 指定されたEventが見つかりません"}})
def count_tickets(group_id:str,event_id:str,db:Session=Depends(db.get_db)):
    event = crud.get_event(db,event_id)
    if not event:
        raise HTTPException(404,"指定されたEventが見つかりません")
    taken_tickets:int=crud.count_tickets_for_event(db,event)
    stock:int=event.ticket_stock
    left_tickets:int=stock-taken_tickets
    return schemas.TicketsNumberData(taken_tickets=taken_tickets,left_tickets=left_tickets,stock=stock)

@app.delete(
    "/groups/{group_id}/events/{event_id}/tickets/{ticket_id}",
    summary="指定された整理券をキャンセル(削除)",
    tags=["tickets"],
    description="### 必要な権限\n指定された整理券のオーナー\n### ログインが必要か\nはい\n",
    responses={"403":{"description":"指定された整理券の所有者である必要があります"}})
def delete_ticket(group_id:str,event_id:str,ticket_id:str,user:schemas.JWTUser=Depends(auth.get_current_user),db:Session=Depends(db.get_db)):
    ticket=crud.get_ticket(db,ticket_id)
    if not ticket.owner_id==user.id:
        raise HTTPException(403,"指定された整理券の所有者である必要があります")
    try:
        crud.delete_ticket(db,ticket)
        return {"OK":True}
    except:
        raise HTTPException(500)

@app.get(
    "/tickets/{ticket_id}",
    response_model=schemas.Ticket,
    summary="指定された整理券の情報を取得",
    tags=["tickets"],
    description="### 必要な権限\nAdmin,当該GroupのOwnerまたはAuthorizer\n### ログインが必要か\nはい\n### 説明\n総当たり攻撃を防ぐため、指定された整理券は存在するが権限が無い場合も404を返す",
    responses={"404":{"description":"- 指定された整理券が見つかりません"}})
def get_ticket(ticket_id:str,user:schemas.JWTUser=Depends(auth.get_current_user),db:Session=Depends(db.get_db)):
    ticket = crud.get_ticket(db,ticket_id)
    if not ticket:
        raise HTTPException(404,"指定された整理券が見つかりません")
    group = crud.get_group_public(db,ticket.group_id)
    if not(crud.check_admin(db,user) or crud.check_owner_of(db,group,user) or crud.check_authorizer_of(db,group,user)):
        raise HTTPException(404,"指定された整理券が見つかりません")
    return ticket


# Tag
@app.post(
    "/tags",
    response_model=List[schemas.Tag],
    summary="新規Tagの作成",
    tags=["tags"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい\n")
def create_tag(tags:List[schemas.TagCreate],permission:schemas.JWTUser = Depends(auth.admin),db:Session=Depends(db.get_db)):
    result=[]
    for tag in tags:
        result.append(crud.create_tag(db,tag))
    return result
@app.get(
    "/tags",
    response_model=List[schemas.Tag],
    summary="全Tagを取得",
    tags=["tags"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ")
def get_all_tags(db:Session=Depends(db.get_db)):
    return crud.get_all_tags(db)
@app.get(
    "/tags/{tag_id}",
    response_model=schemas.Tag,
    summary="指定されたTagを取得",
    tags=["tags"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n",
    responses={"404":{"description":"指定されたTagが見つかりません"}})
def get_tag(tag_id:str,db:Session = Depends(db.get_db)):
    tag_result = crud.get_tag(db,tag_id)
    if not tag_result:
        raise HTTPException(404,"指定されたTagが見つかりません")
    return tag_result
@app.put(
    "/tags/{tag_id}",
    response_model=schemas.Tag,
    summary="Tagの名前を変更",
    tags=["tags"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい",
    responses={"404":{"description":"指定されたTagが見つかりません"}})
def change_tag_name(tag_id:str,tag:schemas.TagCreate,permission:schemas.JWTUser=Depends(auth.admin),db:Session = Depends(db.get_db)):
    tag_result = crud.put_tag(db,tag_id,tag)
    if not tag_result:
        raise HTTPException(404,"指定されたTagが見つかりません")
    return tag_result
@app.delete(
    "/tags/{tag_id}",
    summary="指定されたTagの削除",
    tags=["tags"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい\n",
    responses={"404":{"description":"指定されたTagが見つかりません"}})
def delete_tag(tag_id:str,permission:schemas.JWTUser=Depends(auth.admin),db:Session = Depends(db.get_db)):
    result = crud.delete_tag(db,tag_id)
    if result==None:
        raise HTTPException(404,"指定されたTagが見つかりません")
    return "Successfully Deleted"
    


@app.post(
    "/admin/access_token",
    summary="管理者によるアクセストークンの生成",
    tags=["admin"],
    description="### 必要な権限\nAdmin\n###ログインが必要か\nはい\n###説明\n 管理者権限を持ったアクセストークンを生成します。GitHub Actionsでフロントエンドをビルドするときに使う。")
def create_access_token(additional_data:Union[Dict,None]=None,expire_delta:Union[timedelta,None]=None,user:schemas.JWTUser=Depends(auth.admin)):
    data=additional_data.copy() # additional_dataにgroupsやissやらが含まれてるとまずい気がするから、先にコピー。update()で上書きされる
    data.update({
    "groups":[settings.azure_ad_groups_quaint_admin],
    "iss":"https://api.seiryofes.com/admin/access_token",
    "sub":"access_token_"+user.name,
    "iat":time.time()})
    #TODO DB使って発行したトークンの失効とか出来るようにする？できればした方が良い
    return auth.generate_jwt(data,expire_delta)


#@app.put("/admin/user")
