from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.routers.conversation import get_member_conversation
from app.schemas.agent_task import TaskOut
from app.schemas.message import SendMessage, MessageBody, MessageRole
from app.services import message_service, auth_serivce, broker

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/{session_id}/new", response_model=MessageBody, status_code=status.HTTP_201_CREATED)
def create_message(
    new_message: SendMessage,
    conversation=Depends(get_member_conversation),
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    mentions = message_service.parse_mentions(db, conversation.session_id, new_message.content)
    message = message_service.create_message(
        db, conversation.session_id, new_message.content, MessageRole.user,
        sender_user_id=user_id, mentions=mentions,
    )
    broker.handle(db, conversation, message, acting_user_id=user_id)  # returns immediately
    return message


@router.get("/{session_id}", response_model=list[MessageBody])
def list_messages(
    after: UUID | None = None,
    limit: int = 100,
    conversation=Depends(get_member_conversation),
    db: Session = Depends(get_db),
):
    return message_service.list_messages(db, conversation.session_id, after=after, limit=min(limit, 200))


@router.get("/{session_id}/tasks", response_model=list[TaskOut])
def list_tasks(conversation=Depends(get_member_conversation), db: Session = Depends(get_db)):
    return broker.list_tasks(db, conversation.session_id)


@router.post("/{session_id}/stop")
def stop(
    conversation=Depends(get_member_conversation),
    user_id: UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db),
):
    return {"cancelled": broker.stop(db, conversation.session_id, user_id)}