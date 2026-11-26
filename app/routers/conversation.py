from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.conversation import (
    ConversationCreate, ConversationUpdate, ConversationOut,
    PublicConversationOut, MemberOut, AddAgentBody,
)
from app.services import auth_serivce, conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


def get_member_conversation(
    session_id: UUID,
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    conversation = conversation_service.get_conversation(db, session_id, user_id)
    if not conversation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    return conversation


def get_owner_conversation(
    conversation=Depends(get_member_conversation),
    user_id: UUID = Depends(auth_serivce.current_user_id),
):
    if conversation.user_id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can do this.")
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


@router.get("/public", response_model=list[PublicConversationOut])
def list_public_conversations(
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    return conversation_service.list_public_conversations(db, user_id)


@router.get("/{session_id}", response_model=ConversationOut)
def get_conversation(conversation=Depends(get_member_conversation)):
    return conversation


@router.put("/{session_id}", response_model=ConversationOut)
def update_conversation(
    data: ConversationUpdate,
    conversation=Depends(get_owner_conversation),
    db: Session = Depends(get_db),
):
    return conversation_service.update_conversation(db, conversation, data)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation=Depends(get_owner_conversation),
    db: Session = Depends(get_db),
):
    conversation_service.delete_conversation(db, conversation)


# ---- members ----

@router.post("/{session_id}/join", response_model=ConversationOut)
def join_conversation(
    session_id: UUID,
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    return conversation_service.join_conversation(db, session_id, user_id)


@router.post("/{session_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_conversation(
    conversation=Depends(get_member_conversation),
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    conversation_service.leave_conversation(db, conversation, user_id)


@router.get("/{session_id}/members", response_model=list[MemberOut])
def list_members(
    conversation=Depends(get_member_conversation),
    db: Session = Depends(get_db),
):
    return conversation_service.list_members(db, conversation.session_id)


@router.post("/{session_id}/agents", status_code=status.HTTP_201_CREATED,
             response_model=list[MemberOut])
def add_agent(
    data: AddAgentBody,
    conversation=Depends(get_member_conversation),
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    conversation_service.add_agent(db, conversation, user_id, data.agent_mate_id)
    return conversation_service.list_members(db, conversation.session_id)


@router.delete("/{session_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    member_id: UUID,
    conversation=Depends(get_owner_conversation),
    db: Session = Depends(get_db),
):
    """Kick a user or remove an agent. Owner only."""
    conversation_service.remove_member(db, conversation, member_id)