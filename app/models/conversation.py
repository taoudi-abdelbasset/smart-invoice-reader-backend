import uuid
from app.db.database import Base
from sqlalchemy import Column, Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Conversation(Base):
    __tablename__ = "conversations"

    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(Uuid(as_uuid=True),primary_key=True,default=uuid.uuid4)
    
    title= Column(String)
    
    created_at= Column(DateTime(timezone=True), server_default=func.now())
    deleted_at= Column(DateTime(timezone=True))

    user = relationship("User", back_populates="conversations")
    files = relationship("File", back_populates="conversation")