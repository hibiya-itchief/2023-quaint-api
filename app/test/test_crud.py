from typing_extensions import assert_type
from fastapi.testclient import TestClient
from requests import Session
from app.main import app
from app import crud
from app import schemas
from app.test import factories

client = TestClient(app)

def test_get_user_by_name(db:Session):
    user_in = factories.hogehoge_UserCreateByAdmin()
    crud.create_user_by_admin(db,user_in)
    user = crud.get_user_by_name(db,user_in.username)
    assert user