import datetime
from urllib import response

from app import crud, schemas
from app.main import app
from app.test import factories
from fastapi.testclient import TestClient
from requests import Session
from typing_extensions import assert_type

client = TestClient(app)


def test_read_root_success():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "title": "QUAINT-API",
        "description":"日比谷高校オンライン整理券システム「QUAINT」のAPI"
    }

#もっと細かく書けるかも(https://nmomos.com/tips/2021/03/07/fastapi-docker-8/#toc_id_2)
