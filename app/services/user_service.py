from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth import auth

def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        hashed_password=auth.bcrypt_context.hash(user.password)
    )
    db.add(db_user)
    db.commit()
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