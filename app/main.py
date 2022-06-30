from typing import Optional

<<<<<<< Updated upstream
from fastapi import FastAPI
=======
from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session

from app.cruds import crud
from app.models import models
from app.schemas import schemas

from .database import SessionLocal,engine

#models.Base.metadata.create_all(bind=engine)

description="""
日比谷高校オンライン整理券システム「QUAINT」のAPI
"""
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs."
        
    },
]

app = FastAPI(title="QUAINT-API",description=description,openapi_tags=tags_metadata)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
>>>>>>> Stashed changes



@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}