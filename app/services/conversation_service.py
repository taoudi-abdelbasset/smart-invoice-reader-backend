from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func

from app.models.conversation import Conversation, ConversationVisibility
from app.models.conversation_member import ConversationMember, MemberType, MemberRole
from app.models.file import File as FileModel
from app.models.message import MessageRole
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.services import message_service, agent_service, broker


def _get_member(db: Session, session_id: UUID, user_id: UUID) -> ConversationMember | None:
    return (
        db.query(ConversationMember)
        .filter(ConversationMember.conversation_id == session_id,
                ConversationMember.user_id == user_id)
        .first()
    )


def _member_out(m: ConversationMember) -> dict:
    if m.user:
        name, handle = m.user.username, m.user.username
    elif m.agent:
        name, handle = m.agent.agent_name, m.agent.agent_id
    else:
        name = handle = None
    return {
        "id": m.id, "member_type": m.member_type, "role": m.role,
        "user_id": m.user_id, "agent_mate_id": m.agent_mate_id,
        "name": name, "handle": handle, "joined_at": m.joined_at,
    }


# conversations
def create_conversation(db: Session, user_id: UUID, data: ConversationCreate):
    agent = None
    if data.default_agent_id:
        agent = agent_service.get_agent_by_id(db, data.default_agent_id)
        if not agent:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Agent not found.")

    conversation = Conversation(
        user_id=user_id,
        title=data.title,
        visibility=data.visibility,
        default_agent_id=agent.id if agent else None,
    )
    db.add(conversation)
    db.flush()

    db.add(ConversationMember(
        conversation_id=conversation.session_id, member_type=MemberType.user,
        user_id=user_id, role=MemberRole.owner, added_by=user_id,
    ))
    if agent:
        db.add(ConversationMember(
            conversation_id=conversation.session_id, member_type=MemberType.agent,
            agent_mate_id=agent.id, role=MemberRole.member, added_by=user_id,
        ))
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(db: Session, user_id: UUID):
    """Conversations the user is a member of (own + joined)."""
    return (
        db.query(Conversation)
        .join(ConversationMember, ConversationMember.conversation_id == Conversation.session_id)
        .filter(ConversationMember.user_id == user_id, Conversation.deleted_at.is_(None))
        .order_by(Conversation.created_at.desc())
        .all()
    )


def list_public_conversations(db: Session, user_id: UUID) -> list[dict]:
    counts = (
        db.query(ConversationMember.conversation_id.label("cid"),
                 func.count(ConversationMember.id).label("n"))
        .filter(ConversationMember.member_type == MemberType.user)
        .group_by(ConversationMember.conversation_id)
        .subquery()
    )
    rows = (
        db.query(Conversation, counts.c.n)
        .outerjoin(counts, counts.c.cid == Conversation.session_id)
        .filter(Conversation.visibility == ConversationVisibility.public,
                Conversation.deleted_at.is_(None))
        .order_by(Conversation.created_at.desc())
        .all()
    )
    mine = {cid for (cid,) in db.query(ConversationMember.conversation_id)
            .filter(ConversationMember.user_id == user_id)}
    return [
        {
            "session_id": c.session_id, "title": c.title,
            "owner_username": c.user.username if c.user else None,
            "member_count": n or 0, "is_member": c.session_id in mine,
            "created_at": c.created_at,
        }
        for c, n in rows
    ]


def get_conversation(db: Session, session_id: UUID, user_id: UUID):
    """Returns the conversation only if the user is a member (was: only if owner)."""
    return (
        db.query(Conversation)
        .join(ConversationMember, ConversationMember.conversation_id == Conversation.session_id)
        .filter(Conversation.session_id == session_id,
                ConversationMember.user_id == user_id,
                Conversation.deleted_at.is_(None))
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


# members
def join_conversation(db: Session, session_id: UUID, user_id: UUID):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id, Conversation.deleted_at.is_(None))
        .first()
    )

    if not conversation or conversation.visibility != ConversationVisibility.public:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    if _get_member(db, session_id, user_id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Already a member.")

    db.add(ConversationMember(
        conversation_id=session_id, member_type=MemberType.user,
        user_id=user_id, role=MemberRole.member, added_by=user_id,
    ))
    db.commit()
    return conversation


def leave_conversation(db: Session, conversation: Conversation, user_id: UUID):
    member = _get_member(db, conversation.session_id, user_id)
    if member.role == MemberRole.owner:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The owner can't leave. Delete the conversation instead.")
    db.delete(member)
    db.commit()


def list_members(db: Session, session_id: UUID) -> list[dict]:
    rows = (
        db.query(ConversationMember)
        .options(joinedload(ConversationMember.user), joinedload(ConversationMember.agent))
        .filter(ConversationMember.conversation_id == session_id)
        .order_by(ConversationMember.joined_at.asc())
        .all()
    )
    return [_member_out(m) for m in rows]


def remove_member(db: Session, conversation: Conversation, member_id: UUID):
    """Owner only (checked in the router). Works for users (kick) and agents (remove)."""
    member = (
        db.query(ConversationMember)
        .filter(
            ConversationMember.id == member_id,
            ConversationMember.conversation_id == conversation.session_id
        )
        .first()
    )
    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Member not found.")
    if member.role == MemberRole.owner:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The owner can't be removed.")
    db.delete(member)
    db.commit()


def add_agent(db: Session, conversation: Conversation, user_id: UUID, agent_mate_id: UUID):
    if conversation.visibility == ConversationVisibility.private and conversation.user_id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can add agents here.")

    agent = agent_service.get_agent_by_id(db, agent_mate_id)
    if not agent:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Agent not found.")

    exists = (
        db.query(ConversationMember)
        .filter(ConversationMember.conversation_id == conversation.session_id,
                ConversationMember.agent_mate_id == agent.id)
        .first()
    )
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Agent is already in this conversation.")

    db.add(ConversationMember(
        conversation_id=conversation.session_id, member_type=MemberType.agent,
        agent_mate_id=agent.id, role=MemberRole.member, added_by=user_id,
    ))
    db.commit()

def append_file(db: Session, conversation: Conversation, file: FileModel, user_id: UUID) -> FileModel:
    conversation.files.append(file)
    db.commit()
    db.refresh(file)

    message = message_service.create_message(
        db, conversation.session_id, f"Uploaded {file.file_name}",
        MessageRole.user, sender_user_id=user_id, file_id=file.id,
    )
    broker.handle(db, conversation, message, acting_user_id=user_id)
    return file