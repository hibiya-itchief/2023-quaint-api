from typing_extensions import assert_type
from urllib import response
import datetime
from fastapi.testclient import TestClient
from requests import Session
from app.main import app
from app import crud
from app import schemas
from app.test import factories

client = TestClient(app)


def test_read_root_success():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "title": "QUAINT-API",
        "description":"日比谷高校オンライン整理券システム「QUAINT」のAPI"
    }


def test_login_for_access_token_success(db:Session):#もっと細かく書けるかも(https://nmomos.com/tips/2021/03/07/fastapi-docker-8/#toc_id_2)
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_in.username,
        "password":user_in.password
    })
    assert response.status_code == 200
    
def test_login_for_access_token_fail_username(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":"invalidusername",
        "password":user_in.password
    })
    assert response.status_code == 401
    assert response.json()["detail"]=="Incorrect username or password"
def test_login_for_access_token_fail_password_expired(db:Session):
    user_in = factories.passwordexpired_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_in.username,
        "password":user_in.password
    })
    assert response.status_code == 401
    assert response.json()["detail"]=="Password expired"
def test_login_for_access_token_fail_password(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_in.username,
        "password":"invalidpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"]=="Incorrect username or password"

## User CRUD
def test_create_user_success_by_public(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":"fugafuga",
        "password":"password"
    })
    assert response.status_code == 200

def test_create_user_fail_by_public_short_username(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":"fug",
        "password":"password"
    })
    assert response.status_code == 422
def test_create_user_fail_by_public_long_username(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":"abcdefghijklmnopqrstuvwxyz",##>25
        "password":"password"
    })
    assert response.status_code == 422
def test_create_user_fail_by_public_wrong_username(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":"__!!$@#",
        "password":"password"
    })
    assert response.status_code == 422
def test_create_user_fail_by_public_min_password(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":"fugafuga",
        "password":"passwor"
    })
    assert response.status_code == 422
def test_create_user_fail_by_public_registered_name(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":user_in.username,
        "password":"password"
    })
    assert response.status_code == 400


def test_read_all_users_success(db:Session):
    user_in = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    admin = crud.get_user_by_name(db,user_in.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_in.username,
        "password":user_in.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    response = client.get("/users/",headers=headers)
    assert response.status_code == 200
def test_read_all_users_fail_not_admin(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_in.username,
        "password":user_in.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    response = client.get("/users/",headers=headers)
    assert response.status_code == 403

def test_get_me_success(db:Session):
    user_in = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_in.username,
        "password":user_in.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    response = client.get("/users/me",headers=headers)
    assert response.status_code == 200
    assert response.json()["username"]==user_in.username
def test_get_me_fail(db:Session):
    user_in = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)

    response = client.get("/users/me")
    assert response.status_code == 401

def test_read_my_authority_success(db:Session):
    user_in = factories.Admin_UserCreateByAdmin()
    user = crud.create_user_by_admin(db,user_in)
    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)

    crud.grant_admin(db,user)
    crud.grant_entry(db,user)
    crud.grant_owner_of(db,group,user)
    crud.grant_authorizer_of(db,group,user)

    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_in.username,
        "password":user_in.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    response = client.get("/users/me/authority",headers=headers)
    assert response.status_code == 200
    assert response.json()["is_admin"]==True
    assert response.json()["is_entry"]==True
    assert response.json()["owner_of"][0]==group_in1.id
    assert response.json()["authorizer_of"][0]==group_in1.id


def test_get_list_of_your_tickets(db:Session):
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    user = crud.create_user_by_admin(db,fac_user)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":fac_user.username,
        "password":fac_user.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    crud.create_ticket(db,event1,other_user,person=22)
    response = client.post(
        url="/groups/"+group1.id+"/events/"+event1.id+"/tickets",
        params={
            "person":3
        },
        headers=headers
    )
    assert response.status_code==200

    response = client.get("/users/me/tickets",headers=headers)
    assert response.status_code==200
    assert response.json()[0]["owner_id"]==user.id
    assert response.json()[0]["event_id"]==event1.id
### Change Password
def test_change_password_success(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)

    response = client.put(
        "/users/me/password",
        json={
        "username":user_in.username,
        "password":user_in.password,
        "new_password":"newpassword"
    })
    assert response.status_code == 200
def test_change_password_fail_invalid_name(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)

    response = client.put(
        "/users/me/password",
        json={
        "username":"invalidusername",
        "password":user_in.password,
        "new_password":"newpassword"
    })
    assert response.status_code == 401
def test_change_password_fail_invalid_password(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)

    response = client.put(
        "/users/me/password",
        json={
        "username":user_in.username,
        "password":"invalidpassword",
        "new_password":"newpassword"
    })
    assert response.status_code == 401
def test_change_password_fail_same_password(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)

    response = client.put(
        "/users/me/password",
        json={
        "username":user_in.username,
        "password":user_in.password,
        "new_password":user_in.password
    })
    assert response.status_code == 400
### Authority
def test_grant_authority_success_admin(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    user = crud.get_user_by_name(db,user_in.username)

    response = client.put(
        url="/users/"+user.id+"/authority",
        params={"role":schemas.AuthorityRole.Admin},
        headers=headers
        )
    assert response.status_code == 200
def test_grant_authority_success_entry(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    user = crud.get_user_by_name(db,user_in.username)

    response = client.put(
        url="/users/"+user.id+"/authority",
        params={"role":schemas.AuthorityRole.Entry},
        headers=headers
        )
    assert response.status_code == 200
def test_grant_authority_success_owner(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    user = crud.get_user_by_name(db,user_in.username)

    group_in1=factories.group1_GroupCreateByAdmin()
    crud.create_group(db,group_in1)

    response = client.put(
        url="/users/"+user.id+"/authority",
        params={
            "role":schemas.AuthorityRole.Owner,
            "group_id":group_in1.id
        },
        headers=headers
        )
    assert response.status_code == 200
def test_grant_authority_success_authorizer(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    user = crud.get_user_by_name(db,user_in.username)

    group_in1=factories.group1_GroupCreateByAdmin()
    crud.create_group(db,group_in1)

    response = client.put(
        url="/users/"+user.id+"/authority",
        params={
            "role":schemas.AuthorityRole.Authorizer,
            "group_id":group_in1.id
        },
        headers=headers
        )
    assert response.status_code == 200
def test_grant_authority_fail_not_admin(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    user = crud.get_user_by_name(db,user_in.username)

    group_in1=factories.group1_GroupCreateByAdmin()
    crud.create_group(db,group_in1)

    response = client.put(
        url="/users/"+user.id+"/authority",
        params={
            "role":schemas.AuthorityRole.Owner,
            "group_id":group_in1.id
        },
        headers=headers
        )
    assert response.status_code == 403
def test_grant_authority_fail_owner_authorizer_no_groupid(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    user = crud.get_user_by_name(db,user_in.username)

    group_in1=factories.group1_GroupCreateByAdmin()
    crud.create_group(db,group_in1)

    response = client.put(
        url="/users/"+user.id+"/authority",
        params={
            "role":schemas.AuthorityRole.Owner
        },
        headers=headers
        )
    assert response.status_code == 400
def test_grant_authority_fail_owner_authorizer_group_not_exist(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    user = crud.get_user_by_name(db,user_in.username)

    group_in1=factories.group1_GroupCreateByAdmin()
    crud.create_group(db,group_in1)

    response = client.put(
        url="/users/"+user.id+"/authority",
        params={
            "role":schemas.AuthorityRole.Owner,
            "group_id":"invalidgroupid"
        },
        headers=headers
        )
    assert response.status_code == 404




### Group CRUD
def test_create_group_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    group_in = factories.group1_GroupCreateByAdmin()
    response = client.post(url="/groups",json={
        "id":group_in.id,
        "groupname":group_in.groupname,
        "title":group_in.title,
        "description":group_in.description,
        "page_content":group_in.page_content,
        "enable_vote":group_in.enable_vote
    },headers=headers)
    assert response.status_code==200
    assert response.json()["groupname"]==group_in.groupname
def test_create_group_fail_not_admin(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    group_in = factories.group1_GroupCreateByAdmin()
    response = client.post(url="/groups",json={
        "id":group_in.id,
        "groupname":group_in.groupname,
        "title":group_in.title,
        "description":group_in.description,
        "page_content":group_in.page_content,
        "enable_vote":group_in.enable_vote
    },headers=headers)
    assert response.status_code==403
def test_get_all_groups_success(db:Session):
    group_in1=factories.group1_GroupCreateByAdmin()
    group_in2=factories.group2_GroupCreateByAdmin()
    crud.create_group(db,group_in1)
    crud.create_group(db,group_in2)
    response = client.get(url="/groups")
    assert response.status_code==200
    assert response.json()[0]["groupname"]==group_in1.groupname
    assert response.json()[1]["groupname"]==group_in2.groupname
def test_get_all_groups_success_null(db:Session):
    response = client.get(url="/groups")
    assert response.status_code==200
def test_get_group_success(db:Session):
    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.get("/groups/"+group.id)
    assert response.status_code==200
    assert response.json()["groupname"]==group_in1.groupname
def test_get_group_fail_invalid_id(db:Session):
    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.get("/groups/"+"invalid-id")
    assert response.status_code==404
def test_update_title_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.put("/groups/"+group.id+"/title",params={"title":"ChangedTitle"},headers=headers)
    assert response.status_code==200
    assert response.json()["title"]=="ChangedTitle"
def test_update_title_empty_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.put("/groups/"+group.id+"/title",params={"title":""},headers=headers)
    assert response.status_code==200
    assert response.json()["title"]==""
def test_update_description_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.put("/groups/"+group.id+"/description",params={"description":"ChangedDescription"},headers=headers)
    assert response.status_code==200
    assert response.json()["description"]=="ChangedDescription"
def test_update_description_empty_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.put("/groups/"+group.id+"/description",params={"description":""},headers=headers)
    assert response.status_code==200
    assert response.json()["description"]==""
def test_update_twitter_url_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.put("/groups/"+group.id+"/twitter_url",params={"twitter_url":"https://twitter.com/tucyvub"},headers=headers)
    assert response.status_code==200
    assert response.json()["twitter_url"]=="https://twitter.com/tucyvub"
def test_update_twitter_url_empty_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.put("/groups/"+group.id+"/twitter_url",params={},headers=headers)
    assert response.status_code==200
    assert response.json()["twitter_url"]==None
def test_update_instagram_url_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.put("/groups/"+group.id+"/instagram_url",params={"instagram_url":"http://instagram.com/feZnGP"},headers=headers)
    assert response.status_code==200
    assert response.json()["instagram_url"]=="http://instagram.com/feZnGP"
def test_update_instagram_url_empty_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.put("/groups/"+group.id+"/instagram_url",params={},headers=headers)
    assert response.status_code==200
    assert response.json()["instagram_url"]==None
def test_update_stream_url_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.put("/groups/"+group.id+"/stream_url",params={"stream_url":"http://web.microsoftstream.com/video/test"},headers=headers)
    assert response.status_code==200
    assert response.json()["stream_url"]=="http://web.microsoftstream.com/video/test"
def test_update_stream_url_empty_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.put("/groups/"+group.id+"/stream_url",params={},headers=headers)
    assert response.status_code==200
    assert response.json()["stream_url"]==None
def test_add_tag_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    
    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.put(
        url="/groups/"+group.id+"/tags",
        json={"tag_id":tag.id},
        headers=headers
    )
    assert response.status_code==200
def test_add_tag_fail_invalid_groupid(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    
    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.put(
        url="/groups/"+"invalidgroupid"+"/tags",
        json={"tag_id":tag.id},
        headers=headers
    )
    assert response.status_code==404
def test_add_tag_fail_invalid_tagid(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    
    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.put(
        url="/groups/"+group.id+"/tags",
        json={"tag_id":"invalidtagid"},
        headers=headers
    )
    assert response.status_code==404
def test_add_tag_fail_not_admin(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    
    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.put(
        url="/groups/"+group.id+"/tags",
        json={"tag_id":tag.id},
        headers=headers
    )
    assert response.status_code==403
def test_get_tags_of_group(db:Session):
    group1_in = factories.group1_GroupCreateByAdmin()
    tag1_in = factories.tag1_TagCreateByAdmin()
    tag2_in = factories.tag2_TagCreateByAdmin()
    group1 = crud.create_group(db,group1_in)
    tag1 = crud.create_tag(db,tag1_in)
    tag2 = crud.create_tag(db,tag2_in)
    crud.add_tag(db,group1.id,schemas.GroupTagCreate(tag_id=tag1.id))
    crud.add_tag(db,group1.id,schemas.GroupTagCreate(tag_id=tag2.id))
    response = client.get("/groups/"+group1.id+"/tags")
    assert response.status_code==200
    assert response.json()[0]["tagname"]==tag1_in.tagname
    assert response.json()[1]["tagname"]==tag2_in.tagname

def test_delete_grouptag_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    
    group1_in = factories.group1_GroupCreateByAdmin()
    tag1_in = factories.tag1_TagCreateByAdmin()
    tag2_in = factories.tag2_TagCreateByAdmin()
    group1 = crud.create_group(db,group1_in)
    tag1 = crud.create_tag(db,tag1_in)
    tag2 = crud.create_tag(db,tag2_in)
    crud.add_tag(db,group1.id,schemas.GroupTagCreate(tag_id=tag1.id))
    crud.add_tag(db,group1.id,schemas.GroupTagCreate(tag_id=tag2.id))
    response = client.delete(url="/groups/"+group1.id+"/tags/"+tag1.id,headers=headers)
    assert response.status_code==200

# Event CRUD
def test_create_event_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    group = factories.group1_GroupCreateByAdmin()
    timetable = factories.valid_timetable1()
    db_group = crud.create_group(db,group)
    db_timetable = crud.create_timetable(db,timetable)

    response = client.post(
        url="/groups/"+db_group.id+"/events",
        json={
                "timetable_id":db_timetable.id,
                "ticket_stock":25,
                "lottery":False
            },
        headers=headers)
    assert response.status_code==200
    assert response.json()["group_id"]==db_group.id
    assert response.json()["timetable_id"]==db_timetable.id
def test_create_event_fail_group_not_exist(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    group = factories.group1_GroupCreateByAdmin()
    timetable = factories.valid_timetable1()
    db_group = crud.create_group(db,group)
    db_timetable = crud.create_timetable(db,timetable)

    response = client.post(
        url="/groups/"+"invalidgroupid"+"/events",
        json={
                "timetable_id":db_timetable.id,
                "ticket_stock":25,
                "lottery":False
            },
        headers=headers)
    assert response.status_code==400
def test_create_event_fail_timetable_not_exist(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    group = factories.group1_GroupCreateByAdmin()
    timetable = factories.valid_timetable1()
    db_group = crud.create_group(db,group)
    db_timetable = crud.create_timetable(db,timetable)

    response = client.post(
        url="/groups/"+db_group.id+"/events",
        json={
                "timetable_id":"invalidtimatableid",
                "ticket_stock":25,
                "lottery":False
            },
        headers=headers)
    assert response.status_code==400
def test_create_event_fail_not_admin(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    group = factories.group1_GroupCreateByAdmin()
    timetable = factories.valid_timetable1()
    db_group = crud.create_group(db,group)
    db_timetable = crud.create_timetable(db,timetable)

    response = client.post(
        url="/groups/"+db_group.id+"/events",
        json={
                "timetable_id":db_timetable.id,
                "ticket_stock":25,
                "lottery":False
            },
        headers=headers)
    assert response.status_code==403

def test_get_all_events_success(db:Session):
    group = factories.group1_GroupCreateByAdmin()
    timetable1 = factories.valid_timetable1()
    timetable2 = factories.valid_timetable2()
    db_group = crud.create_group(db,group)
    db_timetable1 = crud.create_timetable(db,timetable1)
    db_timetable2 = crud.create_timetable(db,timetable2)
    db_event1 = crud.create_event(db,db_group.id,schemas.EventCreate(timetable_id=db_timetable1.id,ticket_stock=25,lottery=False))
    db_event2 = crud.create_event(db,db_group.id,schemas.EventCreate(timetable_id=db_timetable2.id,ticket_stock=25,lottery=False))
    response = client.get(url="/groups/"+db_group.id+"/events",)
    assert response.status_code==200
    assert response.json()[0]["timetable_id"]==db_timetable1.id
    assert response.json()[1]["timetable_id"]==db_timetable2.id

def test_get_event_success(db:Session):
    group = factories.group1_GroupCreateByAdmin()
    timetable1 = factories.valid_timetable1()
    db_group = crud.create_group(db,group)
    db_timetable1 = crud.create_timetable(db,timetable1)
    db_event1 = crud.create_event(db,db_group.id,schemas.EventCreate(timetable_id=db_timetable1.id,ticket_stock=25,lottery=False))
    response = client.get(url="/groups/"+db_group.id+"/events/"+db_event1.id,)
    assert response.status_code==200
    assert response.json()["timetable_id"]==db_timetable1.id
def test_delete_event_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    
    group = factories.group1_GroupCreateByAdmin()
    timetable1 = factories.valid_timetable1()
    db_group = crud.create_group(db,group)
    db_timetable1 = crud.create_timetable(db,timetable1)
    db_event1 = crud.create_event(db,db_group.id,schemas.EventCreate(timetable_id=db_timetable1.id,ticket_stock=25,lottery=False))
    response = client.delete(url="/groups/"+db_group.id+"/events/"+db_event1.id,headers=headers)
    assert response.status_code==200
    assert response.json()["OK"]==True
def test_delete_event_fail_dependencies(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    ticket = crud.create_ticket(db,event1,other_user,person=2)
    response = client.delete(url="/groups/"+group1.id+"/events/"+event1.id,headers=headers)
    assert response.status_code==400

# Ticket Crud
def test_create_ticket_success(db:Session):
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    user = crud.create_user_by_admin(db,fac_user)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":fac_user.username,
        "password":fac_user.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    crud.create_ticket(db,event1,other_user,person=22)
    response = client.post(
        url="/groups/"+group1.id+"/events/"+event1.id+"/tickets",
        params={
            "person":3
        },
        headers=headers
    )
    assert response.status_code==200
def test_create_ticket_fail_not_active(db:Session):
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.inactive_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    user = crud.create_user_by_admin(db,fac_user)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":fac_user.username,
        "password":fac_user.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    crud.create_ticket(db,event1,other_user,person=22)
    response = client.post(
        url="/groups/"+group1.id+"/events/"+event1.id+"/tickets",
        params={
            "person":3
        },
        headers=headers
    )
    assert response.status_code==400
def test_create_ticket_fail_not_selling(db:Session):
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    user = crud.create_user_by_admin(db,fac_user)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":fac_user.username,
        "password":fac_user.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=30),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=30),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=90)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    crud.create_ticket(db,event1,other_user,person=22)
    response = client.post(
        url="/groups/"+group1.id+"/events/"+event1.id+"/tickets",
        params={
            "person":3
        },
        headers=headers
    )
    assert response.status_code==404
def test_create_ticket_fail_soldout_stock(db:Session):
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    user = crud.create_user_by_admin(db,fac_user)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":fac_user.username,
        "password":fac_user.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    crud.create_ticket(db,event1,other_user,person=23)
    response = client.post(
        url="/groups/"+group1.id+"/events/"+event1.id+"/tickets",
        params={
            "person":3
        },
        headers=headers
    )
    assert response.status_code==404
def test_create_ticket_fail_soldout_same_timetable(db:Session):
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_group2 = factories.group2_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    user = crud.create_user_by_admin(db,fac_user)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":fac_user.username,
        "password":fac_user.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    group2 = crud.create_group(db,fac_group2)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    event2 = crud.create_event(db,group2.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    crud.create_ticket(db,event1,other_user,person=22)
    response = client.post(
        url="/groups/"+group1.id+"/events/"+event1.id+"/tickets",
        params={
            "person":3
        },
        headers=headers
    )
    response = client.post(
        url="/groups/"+group2.id+"/events/"+event2.id+"/tickets",
        params={
            "person":3
        },
        headers=headers
    )
    assert response.status_code==404
def test_create_ticket_fail_soldout_same_event(db:Session):
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    user = crud.create_user_by_admin(db,fac_user)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":fac_user.username,
        "password":fac_user.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    crud.create_ticket(db,event1,other_user,person=10)
    response = client.post(
        url="/groups/"+group1.id+"/events/"+event1.id+"/tickets",
        params={
            "person":3
        },
        headers=headers
    )
    response = client.post(
        url="/groups/"+group1.id+"/events/"+event1.id+"/tickets",
        params={
            "person":3
        },
        headers=headers
    )
    assert response.status_code==404
def test_create_ticket_fail_invalid_person1(db:Session):
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    user = crud.create_user_by_admin(db,fac_user)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":fac_user.username,
        "password":fac_user.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    crud.create_ticket(db,event1,other_user,person=10)
    response = client.post(
        url="/groups/"+group1.id+"/events/"+event1.id+"/tickets",
        params={
            "person":4
        },
        headers=headers
    )
    assert response.status_code==400
def test_create_ticket_fail_invalid_person2(db:Session):
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    user = crud.create_user_by_admin(db,fac_user)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":fac_user.username,
        "password":fac_user.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    crud.create_ticket(db,event1,other_user,person=10)
    response = client.post(
        url="/groups/"+group1.id+"/events/"+event1.id+"/tickets",
        params={
            "person":-1
        },
        headers=headers
    )
    assert response.status_code==400
def test_create_ticket_fail_invalid_student(db:Session):
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_student_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    user = crud.create_user_by_admin(db,fac_user)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":fac_user.username,
        "password":fac_user.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    crud.create_ticket(db,event1,other_user,person=10)
    response = client.post(
        url="/groups/"+group1.id+"/events/"+event1.id+"/tickets",
        params={
            "person":2
        },
        headers=headers
    )
    assert response.status_code==400

def test_count_tickets_success(db:Session):
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    crud.create_ticket(db,event1,other_user,person=2)
    response = client.get(url="/groups/"+group1.id+"/events/"+event1.id+"/tickets")
    assert response.status_code==200
    assert response.json()["taken_tickets"]==2
    assert response.json()["left_tickets"]==23

def test_get_ticket_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    ticket = crud.create_ticket(db,event1,other_user,person=2)
    response = client.get(url="/tickets/"+ticket.id,headers=headers)
    assert response.status_code==200
    assert response.json()["owner_id"]==other_user.id
def test_get_ticket_fail_not_admin(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    
    fac_group = factories.group1_GroupCreateByAdmin()
    fac_user = factories.active_UserCreateByAdmin()
    fac_other_user = factories.hogehoge_UserCreateByAdmin()
    other_user = crud.create_user_by_admin(db,fac_other_user)
    group1 = crud.create_group(db,fac_group)
    timetable1 = crud.create_timetable(db,schemas.TimetableCreate(
            timetablename="1日目 - 第1公演",
            sell_at=datetime.datetime.now()-datetime.timedelta(minutes=15),
            sell_ends=datetime.datetime.now()+datetime.timedelta(minutes=15),
            starts_at=datetime.datetime.now()+datetime.timedelta(minutes=15),
            ends_at=datetime.datetime.now()+datetime.timedelta(minutes=60)
        ))
    event1 = crud.create_event(db,group1.id,schemas.EventCreate(
            timetable_id=timetable1.id,
            ticket_stock=25,
            lottery=False
        ))
    ticket = crud.create_ticket(db,event1,other_user,person=2)
    response = client.get(url="/tickets/"+ticket.id,headers=headers)
    assert response.status_code==404

# Timetable
def test_create_timetable_success(db:Session):
    timetable = factories.valid_timetable1()
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    response = client.post(
        url="/timetable",
        json={
            "timetablename":timetable.timetablename,
            "sell_at":timetable.sell_at,
            "sell_ends":timetable.sell_ends,
            "starts_at":timetable.starts_at,
            "ends_at":timetable.ends_at
            },
        headers=headers)
    assert response.status_code==200
def test_create_timetable_fail_invalid_date1(db:Session):
    timetable = factories.invalid_timetable1()
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    response = client.post(
        url="/timetable",
        json={
            "timetablename":timetable.timetablename,
            "sell_at":timetable.sell_at,
            "sell_ends":timetable.sell_ends,
            "starts_at":timetable.starts_at,
            "ends_at":timetable.ends_at
            },
        headers=headers)
    assert response.status_code==400
def test_create_timetable_fail_invalid_date2(db:Session):
    timetable = factories.invalid_timetable2()
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    response = client.post(
        url="/timetable",
        json={
            "timetablename":timetable.timetablename,
            "sell_at":timetable.sell_at,
            "sell_ends":timetable.sell_ends,
            "starts_at":timetable.starts_at,
            "ends_at":timetable.ends_at
            },
        headers=headers)
    assert response.status_code==400
def test_create_timetable_fail_invalid_date3(db:Session):
    timetable = factories.invalid_timetable3()
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }

    response = client.post(
        url="/timetable",
        json={
            "timetablename":timetable.timetablename,
            "sell_at":timetable.sell_at,
            "sell_ends":timetable.sell_ends,
            "starts_at":timetable.starts_at,
            "ends_at":timetable.ends_at
            },
        headers=headers)
    assert response.status_code==400
def test_get_all_timetable_success(db:Session):
    timetable1 = factories.valid_timetable1()
    timetable2 = factories.valid_timetable2()
    crud.create_timetable(db,timetable1)
    crud.create_timetable(db,timetable2)
    response = client.get("/timetable")
    assert response.status_code==200
    assert response.json()[0]["timetablename"]== timetable1.timetablename
    assert response.json()[1]["timetablename"]== timetable2.timetablename

def test_get_timetable_success(db:Session):
    timetable=factories.valid_timetable1()
    db_timetable = crud.create_timetable(db,timetable)
    response = client.get(url="/timetable/"+db_timetable.id)
    assert response.status_code==200
    assert response.json()["timetablename"]==timetable.timetablename

###Tag CRUD
def test_create_tag_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    response = client.post(
        url="/tags",
        json={
            "tagname":"tag1"
        },
        headers=headers
    )
    assert response.status_code==200
def test_create_tag_fail_not_admin(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    response = client.post(
        url="/tags",
        json={
            "tagname":"tag1"
        },
        headers=headers
    )
    assert response.status_code==403

def test_get_all_tags_success(db:Session):
    tag_in1 = factories.tag1_TagCreateByAdmin()
    crud.create_tag(db,tag_in1)
    tag_in2 = factories.tag2_TagCreateByAdmin()
    crud.create_tag(db,tag_in2)
    response = client.get(url="/tags")
    assert 200
    assert response.json()[0]["tagname"]==tag_in1.tagname
    assert response.json()[1]["tagname"]==tag_in2.tagname
def test_get_tag_success(db:Session):
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.get(url="/tags/"+tag.id)
    assert response.status_code == 200
def test_get_tag_fail_invalid_id(db:Session):
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.get(url="/tags/"+"invalidid")
    assert response.status_code==404

def test_change_tag_name_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.put(url="/tags/"+tag.id,json={"tagname":"New_name"},headers=headers)
    assert response.status_code==200
    assert response.json()["tagname"]=="New_name"
def test_change_tag_name_fail_invalid_id(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.put(url="/tags/"+"invalidid",json={"tagname":"New_name"},headers=headers)
    assert response.status_code==404
def test_change_tag_name_failed_not_admin(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.put(url="/tags/"+tag.id,json={"tagname":"New_name"},headers=headers)
    assert response.status_code==403

def test_delete_tag_success(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.delete(url="/tags/"+tag.id,headers=headers)
    assert response.status_code==200
def test_delete_tag_fail_invalid_id(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.delete(url="/tags/"+"invaildid",headers=headers)
    assert response.status_code==404
def test_delete_tag_fail_not_admin(db:Session):
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.delete(url="/tags/"+tag.id,headers=headers)
    assert response.status_code==403


### Admin
def test_create_user_by_admin_success(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    user_admin = factories.Admin_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_admin)
    admin = crud.get_user_by_name(db,user_admin.username)
    crud.grant_admin(db,admin)
    response = client.post(
        "/token",
        data={
        "grant_type":"password",
        "username":user_admin.username,
        "password":user_admin.password
    })
    assert response.status_code == 200
    jwt = response.json()
    headers = {
        'Authorization': f'{jwt["token_type"].capitalize()} {jwt["access_token"]}'
    }
    response = client.post(
        url="/admin/users",
        json={
            "username":user_in.username,
            "password":user_in.password,
            "is_student":user_in.is_student,
            "is_family":user_in.is_family,
            "is_active":user_in.is_active,
            "password_expired":user_in.password_expired
        },
        headers=headers
    )
    assert response.status_code == 200
    assert type(response.json()["id"]) is str #hashidsされているか