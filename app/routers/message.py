from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.message import SendMessage, MessageBody, MessageRole
from app.services import message_service,conversation_service
from app.services import auth_serivce

from app.agents.agno_assitant import get_agent

router = APIRouter(prefix="/messages", tags=["messages"])

def get_owned_conversation(
    session_id: UUID,
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    conversation = conversation_service.get_conversation(db, session_id, user_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation

@router.post("/{session_id}/new", response_model=MessageBody, status_code=status.HTTP_201_CREATED)
async def create_message(
    new_message: SendMessage,
    conversation=Depends(get_owned_conversation),
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    message_service.create_message(db, conversation.session_id, new_message.content, MessageRole.user)

    agent = get_agent(user_id=str(user_id), session_id=str(conversation.session_id))
    try:
        response = await agent.arun(new_message.content)
    except Exception:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Agent failed to respond")

    return message_service.create_message(
        db,
        conversation.session_id,
        response.content or "",
        MessageRole.agent,
    )

@router.get("/{session_id}", response_model=list[MessageBody])
def list_messages(
    conversation=Depends(get_owned_conversation),
    db: Session = Depends(get_db),
):
    return message_service.list_messages(db, conversation.session_id)