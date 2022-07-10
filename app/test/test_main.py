from fastapi.testclient import TestClient
from requests import Session
from app.main import app
from app import crud, schemas
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

def test_grant_authority_successfully(db:Session):
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

    request_uri = "/users/"+str(user.id)+"/authority"
    print(request_uri)

    response = client.put(
        url=request_uri,
        params={"role":schemas.AuthorityRole.Authorizer,
        "group_id":1},
        headers=headers
        )
    assert response.status_code == 404
    
    
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
    print(response.json())
    assert response.status_code == 200


def test_get_user_by_name(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    user = crud.get_user_by_name(db,"hogehoge")
    print(user)
    assert user
