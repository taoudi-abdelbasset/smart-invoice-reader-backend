import re
from uuid import UUID
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from app.models.message import Message, MessageRole
from app.models.conversation_member import ConversationMember

MENTION_RE = re.compile(r"(?<![\w@])@([A-Za-z0-9_]+)")

def parse_mentions(db: Session, conversation_id: UUID, content: str) -> list[dict]:
    """Resolve @tags against THIS conversation's members only. Unknown tags are ignored."""
    handles = [h.lower() for h in MENTION_RE.findall(content or "")]
    if not handles:
        return []

    members = (
        db.query(ConversationMember)
        .options(joinedload(ConversationMember.user), joinedload(ConversationMember.agent))
        .filter(ConversationMember.conversation_id == conversation_id)
        .all()
    )
    by_handle = {}
    for m in members:
        if m.user:
            by_handle[m.user.username.lower()] = m
        elif m.agent:
            by_handle[m.agent.agent_id.lower()] = m

    resolved = {}
    for h in handles:
        m = by_handle.get(h)
        if m and h not in resolved:
            resolved[h] = {
                "handle": h,
                "type": m.member_type.value,
                "member_id": str(m.id),
                "user_id": str(m.user_id) if m.user_id else None,
                "agent_mate_id": str(m.agent_mate_id) if m.agent_mate_id else None,
            }
    return list(resolved.values())


def create_message(
    db: Session,
    conversation_id: UUID,
    content: str,
    role: MessageRole = MessageRole.user,
    sender_user_id: UUID | None = None,
    sender_agent_mate_id: UUID | None = None,
    mentions: list | None = None,
    file_id: UUID | None = None,
):
    message = Message(
        conversation_id=conversation_id,
        content=content,
        role=role,
        sender_user_id=sender_user_id,
        sender_agent_mate_id=sender_agent_mate_id,
        mentions=mentions,
        file_id=file_id,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_messages(db: Session, conversation_id: UUID, after: UUID | None = None, limit: int = 100):
    """Oldest first. Pass `after=<last message id>` to get only newer ones (polling)."""
    q = (
        db.query(Message)
        .options(joinedload(Message.sender_user), joinedload(Message.sender_agent))
        .filter(Message.conversation_id == conversation_id, Message.deleted_at.is_(None))
    )
    if after:
        cursor = db.get(Message, after)
        if cursor:
            q = q.filter(or_(
                Message.created_at > cursor.created_at,
                and_(Message.created_at == cursor.created_at, Message.id > cursor.id),
            ))
    return q.order_by(Message.created_at.asc(), Message.id.asc()).limit(limit).all()


def get_message(db: Session, message_id: UUID):
    return db.get(Message, message_id)