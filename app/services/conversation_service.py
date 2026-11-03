from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate


def create_conversation(db: Session, user_id: UUID, data: ConversationCreate):
    conversation = Conversation(user_id=user_id, title=data.title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(db: Session, user_id: UUID):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
        .order_by(Conversation.created_at.desc())
        .all()
    )


def get_conversation(db: Session, session_id: UUID, user_id: UUID):
    return (
        db.query(Conversation)
        .filter(
            Conversation.session_id == session_id,
            Conversation.user_id == user_id,
            Conversation.deleted_at.is_(None),
        )
        .first()
    )


def update_conversation(db: Session, conversation: Conversation, data: ConversationUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(conversation, field, value)
    db.commit()
    db.refresh(conversation)
    return conversation


def delete_conversation(db: Session, conversation: Conversation):
    conversation.deleted_at = func.now()  # soft delete
    db.commit()