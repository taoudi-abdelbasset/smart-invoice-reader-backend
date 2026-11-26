import uuid
from enum import Enum as EnumClass
from app.db.database import Base
from sqlalchemy import Column, Uuid, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class ConversationVisibility(str, EnumClass):
    private = "private"
    public = "public"

class Conversation(Base):
    __tablename__ = "conversations"

    session_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)  # owner

    title = Column(String)
    visibility = Column(Enum(ConversationVisibility), nullable=False,
                        default=ConversationVisibility.private)
    default_agent_id = Column(Uuid(as_uuid=True), ForeignKey("agent_mates.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="conversations")
    default_agent = relationship("MateAgent", foreign_keys=[default_agent_id])
    files = relationship("File", back_populates="conversation")
    messages = relationship("Message", back_populates="conversation")
    members = relationship("ConversationMember", back_populates="conversation")