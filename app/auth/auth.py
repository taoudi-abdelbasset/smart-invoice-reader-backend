from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.dependencies import get_db
from app.schemas.auth import Auth
from app.services import auth_serivce

router = APIRouter(prefix="/auth",tags=["auth"])

bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')

oauth2_bearer= OAuth2PasswordBearer(tokenUrl='auth/token')

@router.post("/token",response_model=Auth)
async def login_access_token(data:Annotated[OAuth2PasswordRequestForm,Depends()] ,db: Session = Depends(get_db)):
    user = auth_serivce.authenticate_user(data.username,data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could Not validate user')
    token = auth_serivce.create_access_token(user.username,user.id,timedelta(minutes=15))
    return {'access_token':token,"token_type":"bearer"}

@router.get("/")
async def get_current_user(user: dict = Depends(auth_serivce.get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="somthing went wrong")
    return user