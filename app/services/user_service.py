from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth import auth

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.models.mate_agent import MateAgent

def create_user(db: Session, user: UserCreate):
    if db.query(MateAgent).filter(func.lower(MateAgent.agent_id) == user.username.lower()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken.")

    db_user = User(
        username=user.username,
        hashed_password=auth.bcrypt_context.hash(user.password),
    )
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken.")
    db.refresh(db_user)
    return db_user

def list_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db:Session, user_id:str):
    user = db.query(User).get(user_id)
    return user

def update_user(db: Session,user_id:int, user: UserCreate):
    updated_user = db.query(User).get(user_id)
    if not updated_user:
        return None
    updated_user.username = user.username   
    db.commit()
    db.refresh(updated_user)
    return updated_user

def delete_user(db: Session, user_id):
    user = db.query(User).get(user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True