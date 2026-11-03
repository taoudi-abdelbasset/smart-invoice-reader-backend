from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.message import SendMessage, MessageBody
from app.services import message_service,conversation_service
from app.routers.conversation import current_user_id

router = APIRouter(prefix="/messages", tags=["messages"])

def get_owned_conversation(
    session_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_db),
):
    conversation = conversation_service.get_conversation(db, session_id, user_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation

@router.post("/{session_id}/new", response_model=MessageBody)
def create_message(
    new_message: SendMessage,
    conversation=Depends(get_owned_conversation),
    db: Session = Depends(get_db)
):
    return message_service.create_message(db, conversation.session_id, new_message)

@router.get("/{session_id}", response_model=list[MessageBody])
def list_messages(
    conversation=Depends(get_owned_conversation),
    db: Session = Depends(get_db),
):
    return message_service.list_messages(db, conversation.session_id)