from typing import Optional,List

from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session

from app.cruds import crud
from app.models import models
from app.schemas import schemas

from .database import SessionLocal,engine

#models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users/",response_model=schemas.User,tags=["users"])
def create_user(user:schemas.UserCreate,db:Session=Depends(get_db)):
    db_user = crud.get_user_by_name(db,username=user.username)
    if db_user:
        raise HTTPException(status_code=400,detail="username already registered")
    return crud.create_user(db=db,user=user)

@app.get("/users/",response_model=List[schemas.User],tags=["users"])
def read_all_users(db:Session=Depends(get_db)):
    users = crud.get_all_users(db)
    return users