from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationOut
from app.services import auth_serivce, conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


def get_owned_conversation(
    session_id: UUID,
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    conversation = conversation_service.get_conversation(db, session_id, user_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.post("/", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def create_conversation(
    data: ConversationCreate,
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    return conversation_service.create_conversation(db, user_id, data)


@router.get("/", response_model=list[ConversationOut])
def list_conversations(
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    return conversation_service.list_conversations(db, user_id)


@router.get("/{session_id}", response_model=ConversationOut)
def get_conversation(conversation=Depends(get_owned_conversation)):
    return conversation


@router.put("/{session_id}", response_model=ConversationOut)
def update_conversation(
    data: ConversationUpdate,
    conversation=Depends(get_owned_conversation),
    db: Session = Depends(get_db),
):
    return conversation_service.update_conversation(db, conversation, data)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation=Depends(get_owned_conversation),
    db: Session = Depends(get_db),
):
    conversation_service.delete_conversation(db, conversation)


# TODO: file upload/attach endpoints (placeholder, added later)
# POST /conversations/{session_id}/files