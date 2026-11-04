from app.core.security import oauth2_bearer, bcrypt_context
from app.models.user import User
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import SECRET_KEY,ALGORITHM
from uuid import UUID
from typing import Annotated
from fastapi import Depends,HTTPException,status

def authenticate_user(username: str,password: str,db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

def create_access_token(username: str,user_id: UUID,expired_at: timedelta):
    encode={
        "sub":username,
        "id":str(user_id)
    }
    expires=datetime.utcnow() + expired_at
    encode.update({"exp":expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        username = payload.get('sub')
        user_id= payload.get('id')
        if user_id is None and username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not found")
        return {
            "username": username,
            "id": user_id
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='somthing went wrong')

async def current_user_id(user: dict = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    return UUID(str(user["id"]))