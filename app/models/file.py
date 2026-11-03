import uuid
from app.db.database import Base
from sqlalchemy import Column, Uuid, String, DateTime, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class File(Base):
    __tablename__="files"
    id= Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(Uuid(as_uuid=True),ForeignKey("conversations.session_id"),nullable=False)

    file_name = Column(String)
    file_path = Column(String)

    # Add procesed feild so the model know what new receite to process  
    is_proccesed = Column(Boolean, default=False)

    created_at= Column(DateTime(timezone=True), server_default=func.now())
    deleted_at= Column(DateTime(timezone=True))

    conversation = relationship("Conversation", back_populates="files")
    invoice = relationship("Invoice", back_populates="file", uselist=False)
