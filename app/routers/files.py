from uuid import UUID
from fastapi import APIRouter, Depends, File as FormFile, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.routers.conversation import current_user_id
from app.schemas.file import UploadedFile
from app.services import conversation_service, file_service

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=UploadedFile, status_code=status.HTTP_201_CREATED)
def upload_new_file(
    conversation_id: UUID = Form(...),
    upload: UploadFile = FormFile(...),
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_db),
):
    conversation = conversation_service.get_conversation(db, conversation_id, user_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    file = file_service.save_file(upload, user_id, conversation_id)
    return conversation_service.append_file(db, conversation, file)