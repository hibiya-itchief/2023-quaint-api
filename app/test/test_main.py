from typing_extensions import assert_type
from fastapi.testclient import TestClient
from requests import Session
from app.main import app
from app import crud
from app import schemas
from app.test import factories

client = TestClient(app)


def test_ルートにアクセス():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "title": "QUAINT-API",
        "description":"日比谷高校オンライン整理券システム「QUAINT」のAPI"
    }


def test_JWTトークンの取得に成功(db:Session):#もっと細かく書けるかも(https://nmomos.com/tips/2021/03/07/fastapi-docker-8/#toc_id_2)
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
    
def test_JWTトークンの取得に失敗_username(db:Session):
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
def test_JWTトークンの取得に失敗_password(db:Session):
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

### User CRUD
def test_create_user_by_public_successfully(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":"fugafuga",
        "password":"password"
    })
    assert response.status_code == 200

def test_create_user_by_public_fail_short_username(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":"fug",
        "password":"password"
    })
    assert response.status_code == 422
def test_create_user_by_public_fail_long_username(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":"abcdefghijklmnopqrstuvwxyz",##>25
        "password":"password"
    })
    assert response.status_code == 422
def test_create_user_by_public_fail_wrong_username(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":"__!!$@#",
        "password":"password"
    })
    assert response.status_code == 422
def test_create_user_by_public_fail_min_password(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":"fugafuga",
        "password":"passwor"
    })
    assert response.status_code == 422
def test_create_user_by_public_fail_registered_name(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    response = client.post(
        "/users",
        json={
        "username":user_in.username,
        "password":"password"
    })
    assert response.status_code == 400
def test_create_user_by_admin(db:Session):
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

def test_read_all_users_successfully(db:Session):
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



def test_change_password_successfully(db:Session):
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
def test_create_group_successfully(db:Session):
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
def test_create_group_failed_not_admin(db:Session):
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
        "groupname":group_in.groupname,
        "title":group_in.title,
        "description":group_in.description,
        "page_content":group_in.page_content,
        "enable_vote":group_in.enable_vote
    },headers=headers)
    assert response.status_code==403
def test_get_all_groups_successfully(db:Session):
    group_in1=factories.group1_GroupCreateByAdmin()
    group_in2=factories.group2_GroupCreateByAdmin()
    crud.create_group(db,group_in1)
    crud.create_group(db,group_in2)
    response = client.get(url="/groups")
    assert response.status_code==200
    assert response.json()[0]["groupname"]==group_in1.groupname
    assert response.json()[1]["groupname"]==group_in2.groupname
def test_get_all_groups_successfully_null(db:Session):
    response = client.get(url="/groups")
    assert response.status_code==200
def test_get_group_successfully(db:Session):
    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.get("/groups/"+group.id)
    assert response.status_code==200
    assert response.json()["groupname"]==group_in1.groupname
def test_get_group_fail_invalid_hashids(db:Session):
    group_in1=factories.group1_GroupCreateByAdmin()
    group = crud.create_group(db,group_in1)
    response = client.get("/groups/"+"invalid-hashids")
    assert response.status_code==404
'''


###Tag CRUD
def test_create_tag_successfully(db:Session):
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

def test_get_all_tags_successfully(db:Session):
    tag_in = factories.tag1_TagCreateByAdmin()
    crud.create_tag(db,tag_in)
    response = client.get(url="/tags")
    assert 200
    assert response.json()[0]["tagname"]==tag_in.tagname
def test_get_tag_successfully(db:Session):
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.get(url="/tags/"+tag.id)
    assert response.status_code == 200
def test_get_tag_failed_invalid_hashids(db:Session):
    tag_in = factories.tag1_TagCreateByAdmin()
    tag = crud.create_tag(db,tag_in)
    response = client.get(url="/tags/"+"invalidhashids")
    assert response.status_code==404

def test_change_tag_name_successfully(db:Session):
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
def test_change_tag_name_failed_invalid_hashids(db:Session):
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
    response = client.put(url="/tags/"+"invalid-hashids",json={"tagname":"New_name"},headers=headers)
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

def test_delete_tag_successfully(db:Session):
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
def test_delete_tag_failed_invalid_hashids(db:Session):
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
    response = client.delete(url="/tags/"+"invaild-hashids",headers=headers)
    assert response.status_code==404
def test_delete_tag_failed_not_admin(db:Session):
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

'''