from app import crud, schemas
from app.main import app
from app.test import factories
from fastapi.testclient import TestClient
from requests import Session
from typing_extensions import assert_type

client = TestClient(app)

