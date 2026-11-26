import uuid
from datetime import datetime, timezone
from enum import Enum as EnumClass
from app.db.database import Base
from sqlalchemy import Column, Uuid, String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship

class MessageRole(str, EnumClass):
    user = "user"
    agent = "agent"
    system = "system"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(Uuid(as_uuid=True), ForeignKey("conversations.session_id"), nullable=False)

    content = Column(String)
    role = Column(Enum(MessageRole), nullable=False)

    sender_user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    sender_agent_mate_id = Column(Uuid(as_uuid=True), ForeignKey("agent_mates.id"), nullable=True)

    mentions = Column(JSON, nullable=True)  # resolved @tags, used by the broker later
    file_id = Column(Uuid(as_uuid=True), ForeignKey("files.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    deleted_at = Column(DateTime(timezone=True))

    conversation = relationship("Conversation", back_populates="messages")
    sender_user = relationship("User", foreign_keys=[sender_user_id])
    sender_agent = relationship("MateAgent", foreign_keys=[sender_agent_mate_id])

    @property
    def sender_name(self) -> str | None:
        if self.sender_user:
            return self.sender_user.username
        if self.sender_agent:
            return self.sender_agent.agent_name
        return None