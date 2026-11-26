import uuid
from datetime import datetime, timezone
from enum import Enum as EnumClass
from app.db.database import Base
from sqlalchemy import Column, Uuid, DateTime, ForeignKey, Enum, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship

class MemberType(str, EnumClass):
    user = "user"
    agent = "agent"

class MemberRole(str, EnumClass):
    owner = "owner"
    member = "member"

class ConversationMember(Base):
    __tablename__ = "conversation_members"
    __table_args__ = (
        UniqueConstraint("conversation_id", "user_id"),
        UniqueConstraint("conversation_id", "agent_mate_id"),
        CheckConstraint("(user_id IS NULL) != (agent_mate_id IS NULL)",
                        name="ck_member_exactly_one"),
    )

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(Uuid(as_uuid=True), ForeignKey("conversations.session_id"), nullable=False)

    member_type = Column(Enum(MemberType), nullable=False)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    agent_mate_id = Column(Uuid(as_uuid=True), ForeignKey("agent_mates.id"), nullable=True)

    role = Column(Enum(MemberRole), nullable=False, default=MemberRole.member)
    added_by = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    agent = relationship("MateAgent", foreign_keys=[agent_mate_id])