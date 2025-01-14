from typing import Annotated
from database import SessionLocal
from fastapi import APIRouter,Depends
from pydantic import BaseModel,Field
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from  fastapi.security import OAuth2PasswordRequestForm

router=APIRouter()

bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')

class UserRequest(BaseModel):
    email:str
    username:str
    first_name:str
    last_name:str
    password:str
    is_active:bool=Field(default=True)
    role:str

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]

def authenticate_user(username:str,password:str,db):
    user=db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return True

@router.post("/auth/")
async def create_user(db:db_dependency,create_user_request:UserRequest):
    create_user=Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=create_user_request.is_active,
        role=create_user_request.role
    )

    db.add(create_user)
    db.commit()
    return  (create_user)

@router.post("/token")
def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    user=authenticate_user(form_data.username,form_data.password,db)
    if not user:
        return 'Failed Authentication'
    return 'Successful Authentication'

@router.get("/users")
def read_user(db:Annotated[Session,Depends(get_db)]):
    return db.query(Users).all()