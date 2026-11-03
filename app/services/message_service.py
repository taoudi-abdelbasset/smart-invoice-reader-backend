from uuid import UUID
from sqlalchemy.orm import Session

from app.models.message import Message
from app.schemas.message import SendMessage, MessageRole


def create_message(db: Session, conversation_id: UUID, data: SendMessage):
    message = Message(conversation_id=conversation_id, content=data.content, role=MessageRole.user)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_messages(db: Session, conversation_id: UUID):
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .all()
    )


def get_message(db: Session, message_id: UUID):
    return (
        db.query(Message)
        .get(message_id)
        .first()
    )