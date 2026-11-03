import uuid
from enum import Enum as EnumClass
from app.db.database import Base
from sqlalchemy import Column, Uuid, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class MessageRole(str, EnumClass):
    user = "user"
    agent = "agent"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Uuid(as_uuid=True),primary_key=True,default=uuid.uuid4)
    conversation_id = Column(Uuid(as_uuid=True), ForeignKey("conversations.session_id"), nullable=False)
    
    content = Column(String)

    role = Column(Enum(MessageRole), nullable=False)
    
    created_at= Column(DateTime(timezone=True), server_default=func.now())
    deleted_at= Column(DateTime(timezone=True))

    conversation = relationship("Conversation", back_populates="messages")