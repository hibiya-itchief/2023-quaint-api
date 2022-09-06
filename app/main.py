from datetime import datetime,timedelta
from typing import Optional,List,Union
from xml.dom.minidom import Entity

from fastapi import FastAPI,Depends,HTTPException,status,File,UploadFile,Query,Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import Field

from app import schemas,dep,models,crud,storage


from .database import SessionLocal, engine


#models.Base.metadata.create_all(bind=engine)

description="""
日比谷高校オンライン整理券システム「QUAINT」のAPI \n
<a href="https://seiryofes.com">seiryofes.com</a>
<a href="https://github.com/hibiya-itchief/quaint-api">GitHub</a>
"""
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
        "name":"timetable",
        "description":"Timetable : 公演の時間帯情報"
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


@app.get("/")
def read_root():
    return {
        "title": "QUAINT-API",
        "description":"日比谷高校オンライン整理券システム「QUAINT」のAPI"
    }

@app.post(
    "/users/me/login",
    response_model=schemas.Token,
    summary="ログインしてアクセストークンを取得する",
    tags=["users"],
    description="### 必要な権限\nなし\n### ログインが必要か\n--",
    response_description="ログインに成功",
    responses={"401":{"description":"- ユーザー名かパスワードが間違っています\n- パスワードが失効しています。新しいパスワードを設定してください。"}})
async def login_for_access_token(db:Session = Depends(dep.get_db),form_data: OAuth2PasswordRequestForm = Depends()):
    return dep.login_for_access_token(form_data.username,form_data.password,db)

@app.post(
    "/users",
    response_model=schemas.Token,
    summary="新規ユーザー作成",
    tags=["users"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n### 説明\n誰でも新規ユーザーを作成できる。ただし、この時点では何の権限も与えられないので何もできない\nフラグや権限も設定してユーザーを作成したい場合は/admin/users [POST]",
    response_description="ユーザーが作成されました",
    responses={"400":{"description":"ユーザー名は既に使用されています"}})
def create_user(user:schemas.UserCreate,db:Session=Depends(dep.get_db)):
    db_user = crud.get_user_by_name(db,username=user.username)
    if db_user:
        raise HTTPException(status_code=400,detail="ユーザー名は既に使用されています")
    crud.create_user(db=db,user=user)
    return dep.login_for_access_token(user.username,user.password,db)
@app.get(
    "/users",
    response_model=List[schemas.User],
    summary="全ユーザーの情報を取得",
    tags=["users"],
    description="### 必要な権限\n**Admin\n### ログインが必要か\nはい",)
def read_all_users(permission:schemas.User = Depends(dep.admin),db:Session=Depends(dep.get_db)):
    users = crud.get_all_users(db)
    return users

@app.get(
    "/users/me",
    response_model=schemas.User,
    summary="ログイン中のユーザーの情報を取得",
    tags=["users"],
    description="### 必要な権限\nなし\n### ログインが必要か\nはい")
def get_me(user:schemas.User = Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    return user
@app.get(
    "/users/me/authority",
    response_model=schemas.UserAuthority,
    summary="ログイン中のユーザーの権限を取得",
    tags=["users"],
    description="### 必要な権限\nなし\n### ログインが必要か\nはい")
def read_my_authority(user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    return schemas.UserAuthority(
        user_id=user.id,
        is_admin=crud.check_admin(db,user),
        is_entry=crud.check_entry(db,user),
        owner_of=crud.get_owner_list(db,user),
        authorizer_of=crud.get_authorizer_list(db,user))
@app.put(
    "/users/me/password",
    tags=["users"],
    summary="ログイン中のユーザーのパスワードを変更",
    description="### 必要な権限\nなし\n### ログインが必要か\n--",
    response_description="パスワードが正しく変更されました",
    responses={"400":{"description":"新しいパスワードには現在のものとは違うパスワードを設定してください"},
        "401":{"description":"ユーザー名またはパスワードが間違っています"}})
def change_password(user:schemas.PasswordChange,db:Session=Depends(dep.get_db)):
    if not dep.authenticate_user(db,user.username,user.password):
        raise HTTPException(401,"ユーザー名またはパスワードが間違っています")
    if user.password==user.new_password:
        raise HTTPException(400,"新しいパスワードには現在のものとは違うパスワードを設定してください")
    crud.change_password(db,user)
    return HTTPException(200,"パスワードが正しく変更されました")


@app.get(
    "/users/me/tickets",
    response_model=List[schemas.Ticket],
    summary="ログイン中のユーザーが所有している整理券のリストを取得",
    tags=["users"],
    description="### 必要な権限\nなし\n### ログインが必要か\nはい")
def get_list_of_your_tickets(user:schemas.User = Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    return crud.get_list_of_your_tickets(db,user)

@app.put(
    "/users/{user_id}/activation",
    response_model=schemas.User,
    summary="ユーザーのアクティベート",
    tags=["users"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい\n")
def activate_user(user_id:str,permission:schemas.User=Depends(dep.admin),db:Session=Depends(dep.get_db)):
    user=crud.get_user(db,user_id)
    if not user:
        raise HTTPException(404,"ユーザーが見つかりません")
    return crud.activate_user(db,user)

@app.put(
    "/users/{user_id}/authority",
    summary="ユーザーに権限を与える",
    tags=["users"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい",
    responses={"404":{"description":"- 指定されたユーザーが見つかりません\n- 指定されたGroupが見つかりません"},"400":{"description":"Owner,Authorizeの権限を付与するにはgroup_idの指定が必要です。"}})
def grant_authority(user_id:str,role:schemas.AuthorityRole=Body(),group_id:Union[str,None]=Body(default=None),permission:schemas.User=Depends(dep.admin),db:Session=Depends(dep.get_db)):
    user=crud.get_user(db,user_id)
    if not user:
        raise HTTPException(404,"指定されたユーザーが見つかりません")

    if role ==schemas.AuthorityRole.Admin:
        if crud.check_admin(db,user):
            raise HTTPException(200)
        return crud.grant_admin(db,user)
    elif role == schemas.AuthorityRole.Entry:
        if crud.check_entry(db,user):
            raise HTTPException(200)
        return crud.grant_entry(db,user)
    else:
        if not group_id:
            raise HTTPException(400,"Owner,Authorizeの権限を付与するにはgroup_idの指定が必要です。")
        group = crud.get_group(db,group_id)
        if not group:
            raise HTTPException(404,"指定されたGroupが見つかりません")
        if role == schemas.AuthorityRole.Owner:
            if crud.check_owner_of(db,group,user):
                raise HTTPException(200)
            return crud.grant_owner_of(db,group,user)
        elif role == schemas.AuthorityRole.Authorizer:
            if crud.check_authorizer_of(db,group,user):
                raise HTTPException(200)
            return crud.grant_authorizer_of(db,group,user)



@app.post(
    "/groups",
    response_model=List[schemas.Group],
    summary="新規Groupの作成",
    tags=["groups"],
    description='### 必要な権限\nAdmin\n### ログインが必要か\nはい\n### 説明\n- オブジェクトではなく配列の形でjsonを渡してください\n- 複数のGroupの一括作成ができます\n- 各種URLを指定せずに作成する場合は、"twitter_url":""のように空文字ではなくパラメータ自体をjsonに記述せずNoneにしてください',)
def create_group(groups:List[schemas.GroupCreate],permission:schemas.User=Depends(dep.admin),db:Session=Depends(dep.get_db)):
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
def get_all_groups(db:Session=Depends(dep.get_db)):
    return crud.get_all_groups(db)
@app.get(
    "/groups/{group_id}",
    response_model=schemas.Group,
    summary="指定されたGroupの情報を取得",
    tags=["groups"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ",
    responses={"404":{"description":"指定されたGroupが見つかりません"}})
def get_group(group_id:str,db:Session=Depends(dep.get_db)):
    group_result = crud.get_group(db,group_id)
    if not group_result:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    return group_result

@app.put(
    "/groups/{group_id}/title",
    response_model=schemas.Group,
    summary="指定されたGroupの演目名を変更",
    tags=["groups"],
    description="### 必要な権限\nAdmin,当該GroupのOwner\n### ログインが必要か\nはい",
    responses={"404":{"description":"指定されたGroupが見つかりません"},
        "401":{"description":"Adminまたは当該GroupのOwnerの権限が必要です"}})
def update_title(group_id:str,title:Union[str,None]=Query(default=None,max_length=50),user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    if not(crud.check_admin(db,user) or crud.check_owner_of(db,group,user)):
        raise HTTPException(401,"Adminまたは当該GroupのOwnerの権限が必要です")
    return crud.update_title(db,group,title)
@app.put(
    "/groups/{group_id}/description",
    response_model=schemas.Group,
    summary="指定されたGroupの説明文を変更",
    tags=["groups"],
    description="### 必要な権限\nAdmin,当該GroupのOwner\n### ログインが必要か\nはい",
    responses={"404":{"description":"指定されたGroupが見つかりません"},
        "401":{"description":"Adminまたは当該GroupのOwnerの権限が必要です"}})
def update_description(group_id:str,description:Union[str,None]=Query(default=None,max_length=200),user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    if not(crud.check_admin(db,user) or crud.check_owner_of(db,group,user)):
        raise HTTPException(401,"Adminまたは当該GroupのOwnerの権限が必要です")
    return crud.update_description(db,group,description)
@app.put(
    "/groups/{group_id}/twitter_url",
    response_model=schemas.Group,
    summary="指定されたGroupのtwitter_urlを変更",
    tags=["groups"],
    description="### 必要な権限\nAdmin,当該GroupのOwner\n### ログインが必要か\nはい",
    responses={"404":{"description":"指定されたGroupが見つかりません"},
        "401":{"description":"Adminまたは当該GroupのOwnerの権限が必要です"}})
def update_twitter_url(group_id:str,twitter_url:Union[str,None]=Query(default=None,regex="https?://twitter\.com/[0-9a-zA-Z_]{1,15}/?"),user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    if not(crud.check_admin(db,user) or crud.check_owner_of(db,group,user)):
        raise HTTPException(401,"Adminまたは当該GroupのOwnerの権限が必要です")
    return crud.update_twitter_url(db,group,twitter_url)
@app.put(
    "/groups/{group_id}/instagram_url",
    response_model=schemas.Group,
    summary="指定されたGroupのinstagram_urlを変更",
    tags=["groups"],
    description="### 必要な権限\nAdmin,当該GroupのOwner\n### ログインが必要か\nはい",
    responses={"404":{"description":"指定されたGroupが見つかりません"},
        "401":{"description":"Adminまたは当該GroupのOwnerの権限が必要です"}})
def update_instagram_url(group_id:str,instagram_url:Union[str,None]=Query(default=None,regex="https?://instagram\.com/[0-9a-zA-Z_.]{1,30}/?"),user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    if not(crud.check_admin(db,user) or crud.check_owner_of(db,group,user)):
        raise HTTPException(401,"Adminまたは当該GroupのOwnerの権限が必要です")
    return crud.update_instagram_url(db,group,instagram_url)
@app.put(
    "/groups/{group_id}/stream_url",
    response_model=schemas.Group,
    summary="指定されたGroupのstream_urlを変更",
    tags=["groups"],
    description="### 必要な権限\nAdminr\n### ログインが必要か\nはい",
    responses={"404":{"description":"指定されたGroupが見つかりません"},
        "401":{"description":"Adminの権限が必要です"}})
def update_stream_url(group_id:str,stream_url:Union[str,None]=Query(default=None,regex="https?://web\.microsoftstream\.com/video/[\w!?+\-_~=;.,*&@#$%()'[\]]+/?"),user:schemas.User=Depends(dep.admin),db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    if not crud.check_admin(db,user):
        raise HTTPException(401,"Adminの権限が必要です")
    return crud.update_stream_url(db,group,stream_url)

@app.put(
    "/groups/{group_id}/thumbnail_image",
    response_model=schemas.Group,
    summary="指定されたGroupのサムネイル画像を変更",
    tags=["groups"],
    description="### 必要な権限\nAdmin,当該GroupのOwner\n### ログインが必要か\nはい",
    responses={"404":{"description":"指定されたGroupが見つかりません"},
        "401":{"description":"Adminまたは当該GroupのOwnerの権限が必要です"}})
def upload_thumbnail_image(group_id:str,file:Union[bytes,None] = File(default=None),user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    if not(crud.check_admin(db,user) or crud.check_owner_of(db,group,user)):
        raise HTTPException(401,"Adminまたは当該GroupのOwnerの権限が必要です")
    if group.thumbnail_image_url:
            storage.delete_image(group.thumbnail_image_url)
    if file:
        image_url = storage.upload_to_oos(file)
        return crud.update_thumbnail_image_url(db,group,image_url)
    else:
        return crud.update_thumbnail_image_url(db,group,None)
@app.put(
    "/groups/{group_id}/cover_image",
    response_model=schemas.Group,
    summary="指定されたGroupのカバー画像を変更",
    tags=["groups"],
    description="### 必要な権限\nAdmin,当該GroupのOwner\n### ログインが必要か\nはい",
    responses={"404":{"description":"指定されたGroupが見つかりません"},
        "401":{"description":"Adminまたは当該GroupのOwnerの権限が必要です"}})
def upload_cover_image(group_id:str,file:Union[bytes,None] = File(default=None),user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    if not(crud.check_admin(db,user) or crud.check_owner_of(db,group,user)):
        raise HTTPException(401,"Adminまたは当該GroupのOwnerの権限が必要です")
    if group.cover_image_url:
            storage.delete_image(group.cover_url)
    if file:
        image_url = storage.upload_to_oos(file)
        return crud.update_cover_image_url(db,group,image_url)
    else:
        return crud.update_cover_image_url(db,group,None)

@app.put(
    "/groups/{group_id}/tags",
    summary="指定されたGroupにタグを紐づける",
    tags=["groups"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい",
    responses={"404":{"description":"指定されたGroupまたはTagが見つかりません"}})
def add_tag(group_id:str,tag_id:schemas.GroupTagCreate,permission:schemas.User=Depends(dep.admin),db:Session=Depends(dep.get_db)):
    grouptag = crud.add_tag(db,group_id,tag_id)
    if not grouptag:
        raise HTTPException(404,"指定されたGroupまたはTagが見つかりません")
    return "Add Tag Successfully"
@app.get(
    "/groups/{group_id}/tags",
    response_model=List[schemas.Tag],
    summary="指定されたGroupに紐づけられているTagを取得",
    tags=["groups"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n",
    responses={"404":{"description":"指定されたGroupが見つかりません"}})
def get_tags_of_group(group_id:str,db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    return crud.get_tags_of_group(db,group)
@app.delete(
    "/groups/{group_id}/tags/{tag_id}",
    summary="指定されたGroupに紐づいている指定されたTagを削除",
    tags=["groups"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい\n",
    responses={"404":{"description":"- 指定されたGroupが見つかりません\n- 指定されたTagが見つかりません"}})
def delete_grouptag(group_id:str,tag_id:str,permission:schemas.User=Depends(dep.admin),db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    tag = crud.get_tag(db,tag_id)
    if not tag:
        raise HTTPException(404,"指定されたTagが見つかりません")
    return crud.delete_grouptag(db,group,tag)
@app.delete(
    "/groups/{group_id}",
    summary="指定されたGroupを削除",
    tags=["groups"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい\n### 説明\n指定するGroupに紐づけられているEvent,Ticket,Tagをすべて削除しないと削除できません",
    responses={"404":{"description":"指定されたGroupが見つかりません"},
        "400":{"description":"指定されたGroupに紐づけられているEvent,Ticket,Tagをすべて削除しないと削除できません"}})
def delete_group(group_id:str,permission:schemas.User=Depends(dep.admin),db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    try:
        crud.delete_group(db,group)
        return {"OK":True}
    except:
        raise HTTPException(400,"指定されたGroupに紐づけられているEvent,Ticket,Tagをすべて削除しないと削除できません")


@app.get(
    "/search",
    response_model=List[schemas.Group],
    summary="Groupを検索",
    tags=["groups"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n### 説明\n団体名・演目名・説明文に、qに与えられた文字列を含んでいるGroupのListが返されます")
def search_groups(q:str,db:Session=Depends(dep.get_db)):
    return crud.search_groups(db,q)



### Event Crud
@app.post(
    "/groups/{group_id}/events",
    response_model=List[schemas.Event],
    summary="新規Eventを作成",
    tags=["events"],
    description="### 必要な権限\nAdmin,当該GroupのOwner\n### ログインが必要か\nはい\n### 説明\n- 複数Eventを一括作成できます",
    responses={"400":{"description":"パラメーターが不適切です"},
        "403":{"description":"Adminまたは当該GroupのOwnerの権限が必要です"},
        "404":{"description":"指定されたGroupが見つかりません"}})
def create_event(group_id:str,events:List[schemas.EventCreate],user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    if not(crud.check_admin(db,user) or crud.check_owner_of(db,group,user)):
        raise HTTPException(403,"Adminまたは当該GroupのOwnerの権限が必要です")
    result=[]
    for event in events:
        if crud.check_same_event(db,group.id,event.timetable_id):
            raise HTTPException(400,"ひとつの団体が同一時間帯で2つ以上の公演を作ることはできません")
        event = crud.create_event(db,group_id,event)
        if not event:
            raise HTTPException(400,"パラメーターが不適切です")
        result.append(event)
    return result
@app.get(
    "/groups/{group_id}/events",
    response_model=List[schemas.Event],
    summary="指定されたGroupの全Eventを取得",
    tags=["events"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n")
def get_all_events(group_id:str,db:Session=Depends(dep.get_db)):
    return crud.get_all_events(db,group_id)
@app.get(
    "/groups/{group_id}/events/{event_id}",
    response_model=schemas.Event,
    summary="指定されたGroupの指定されたEevntを取得",
    tags=["events"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n",
    responses={"404":{"description":"指定されたGroupまたはEventが見つかりません"}})
def get_event(group_id:str,event_id:str,db:Session=Depends(dep.get_db)):
    event = crud.get_event(db,group_id,event_id)
    if not event:
        raise HTTPException(404,"指定されたGroupまたはEventが見つかりません")
    return event
@app.delete(
    "/groups/{group_id}/events/{event_id}",
    summary="指定されたGroupの指定されたEventを削除",
    tags=["events"],
    description="### 必要な権限\nAdmin,当該GroupのOwner\n### ログインが必要か\nはい\n### 説明\n指定するEventに紐づけられたTicketを全て削除しないと削除できません",
    responses={"404":{"description":"指定されたGroupまたはEventがありません"},
        "403":{"description":"Adminまたは当該GroupのOwnerの権限が必要です"},
        "400":{"description":"指定されたEventに紐づけられたTicketを全て削除しないと削除できません"}})
def delete_events(group_id:str,event_id:str,user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    event = crud.get_event(db,group_id,event_id)
    if not event:
        raise HTTPException(404,"指定されたGroupまたはEventがありません")
    group = crud.get_group(db,event.group_id)
    if not(crud.check_admin(db,user) or crud.check_owner_of(db,group,user)):
        raise HTTPException(403,"Adminまたは当該GroupのOwnerの権限が必要です")
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
def create_ticket(group_id:str,event_id:str,person:int,user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    if user.is_active:#学校に来場しているか
        event = crud.get_event(db,group_id,event_id)
        if not event:
            raise HTTPException(404,"指定されたGroupまたはEventが見つかりません")
        timetable = crud.get_timetable(db,event.timetable_id)
        if timetable.sell_at <= datetime.now() and datetime.now() <= timetable.sell_ends:
            if crud.count_tickets_for_event(db,event)+person<=event.ticket_stock and crud.check_double_ticket(db,event,user):##まだチケットが余っていて、同時間帯の公演の整理券取得ではない
                if user.is_student==False and 0<person<4:#一般アカウント(家族アカウント含む)は1アカウントにつき3人まで入れる
                    return crud.create_ticket(db,event,user,person)
                elif user.is_student and person==1:
                    return crud.create_ticket(db,event,user,person)
                else:
                    raise HTTPException(400,"同時入場人数は3人まで(本校生徒は1人)までです")
            elif not crud.check_double_ticket(db,event,user):
                raise HTTPException(404,"既にこの公演・この公演と同じ時間帯の公演の整理券を取得している場合、新たに取得はできません")
            else:
                raise HTTPException(404,"この公演の整理券は売り切れています")
        else:
            raise HTTPException(404,"現在整理券の配布時間外です")
    else:
        raise HTTPException(400,"校内への来場処理をしたユーザーのみが整理券を取得できます")
@app.get(
    "/groups/{group_id}/events/{event_id}/tickets",
    response_model=schemas.TicketsNumberData,
    summary="指定された公演の整理券の枚数情報を取得",
    tags=["tickets"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n",
    responses={"404":{"description":"- 指定されたGroupが見つかりません\n- 指定されたEventが見つかりません"}})
def count_tickets(group_id:str,event_id:str,db:Session=Depends(dep.get_db)):
    group = crud.get_group(db,group_id)
    if not group:
        raise HTTPException(404,"指定されたGroupが見つかりません")
    event = crud.get_event(db,group.id,event_id)
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
def delete_ticket(group_id:str,event_id:str,ticket_id:str,user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
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
def get_ticket(ticket_id:str,user:schemas.User=Depends(dep.get_current_user),db:Session=Depends(dep.get_db)):
    ticket = crud.get_ticket(db,ticket_id)
    if not ticket:
        raise HTTPException(404,"指定された整理券が見つかりません")
    group = crud.get_group(db,ticket.group_id)
    if not(crud.check_admin(db,user) or crud.check_owner_of(db,group,user) or crud.check_authorizer_of(db,group,user)):
        raise HTTPException(404,"指定された整理券が見つかりません")
    return ticket


# Timetable
@app.post(
    "/timetable",
    response_model=List[schemas.Timetable],
    summary="新規Timetableの作成",
    tags=["timetable"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい\n### 説明\nEventは直接時間の情報を持たず、このTimetableのidで紐づける",
    responses={"400":{"description":"パラメーターが不適切です"}})
def create_timetable(timetables:List[schemas.TimetableCreate],permission:schemas.User = Depends(dep.admin),db:Session=Depends(dep.get_db)):
    results=[]
    for timetable in timetables:
        result = crud.create_timetable(db,timetable=timetable)
        if not result:
            raise HTTPException(400,"パラメーターが不適切です")
        results.append(result)
    return results
@app.get(
    "/timetable",
    response_model=List[schemas.Timetable],
    summary="全Timetableを取得",
    tags=["timetable"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ")
def get_all_timetable(db:Session=Depends(dep.get_db)):
    return crud.get_all_timetable(db)
@app.get(
    "/timetable/{timetable_id}",
    response_model=schemas.Timetable,
    summary="指定されたTimetableの情報を取得",
    tags=["timetable"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n",
    responses={"404":{"description":"指定されたTimetableが見つかりません"}})
def get_timetable(timetable_id:str,db:Session=Depends(dep.get_db)):
    timetable = crud.get_timetable(db,timetable_id)
    if not timetable:
        raise HTTPException(404,"指定されたTimetableが見つかりません")
    return timetable

# Tag
@app.post(
    "/tags",
    response_model=List[schemas.Tag],
    summary="新規Tagの作成",
    tags=["tags"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい\n")
def create_tag(tags:List[schemas.TagCreate],permission:schemas.User = Depends(dep.admin),db:Session=Depends(dep.get_db)):
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
def get_all_tags(db:Session=Depends(dep.get_db)):
    return crud.get_all_tags(db)
@app.get(
    "/tags/{tag_id}",
    response_model=schemas.Tag,
    summary="指定されたTagを取得",
    tags=["tags"],
    description="### 必要な権限\nなし\n### ログインが必要か\nいいえ\n",
    responses={"404":{"description":"指定されたTagが見つかりません"}})
def get_tag(tag_id:str,db:Session = Depends(dep.get_db)):
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
def change_tag_name(tag_id:str,tag:schemas.TagCreate,permission:schemas.User=Depends(dep.admin),db:Session = Depends(dep.get_db)):
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
def delete_tag(tag_id:str,permission:schemas.User=Depends(dep.admin),db:Session = Depends(dep.get_db)):
    result = crud.delete_tag(db,tag_id)
    if result==None:
        raise HTTPException(404,"指定されたTagが見つかりません")
    return "Successfully Deleted"
    


@app.post(
    "/admin/users",
    response_model=List[schemas.User],
    summary="管理者によるユーザーの作成",
    tags=["admin"],
    description="### 必要な権限\nAdmin\n### ログインが必要か\nはい\n### 説明\n フラグや権限を指定して一括作成できます。",
    responses={"400":{"description":"ユーザー名が既に使われています"}})
def create_user_by_admin(users:List[schemas.UserCreateByAdmin],permission:schemas.User = Depends(dep.admin),db:Session=Depends(dep.get_db)):
    result=[]
    for user in users:
        db_user = crud.get_user_by_name(db,username=user.username)
        if db_user:
            raise HTTPException(status_code=400,detail="ユーザー名が既に使われています")
        result.append(crud.create_user_by_admin(db=db,user=user))
    return result



#@app.put("/admin/user")