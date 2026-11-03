from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.user import UserCreate, UserOut
from app.services import user_service
from uuid import UUID

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)

@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return user_service.list_users(db)

@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(user_id:UUID, db: Session = Depends(get_db)):
    return user_service.get_user_by_id(db, user_id=user_id)

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id:UUID,user: UserCreate, db: Session = Depends(get_db)):
    return user_service.update_user(db,user_id=user_id,user=user)

@router.delete("/{user_id}")
def delete_user(user_id:UUID, db: Session = Depends(get_db)):
    return {"success":user_service.delete_user(db,user_id=user_id)}