from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.user import UserCreate, UserOut
from app.services import user_service, auth_serivce

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)


@router.get("/", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_id: UUID = Depends(auth_serivce.current_user_id),
):
    return user_service.list_users(db)


@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_id: UUID = Depends(auth_serivce.current_user_id),
):
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: UUID,
    user: UserCreate,
    db: Session = Depends(get_db),
    current_id: UUID = Depends(auth_serivce.current_user_id),
):
    if user_id != current_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only edit your own account.")
    updated = user_service.update_user(db, user_id=user_id, user=user)
    if not updated:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    return updated


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_id: UUID = Depends(auth_serivce.current_user_id),
):
    if user_id != current_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only delete your own account.")
    return {"success": user_service.delete_user(db, user_id=user_id)}