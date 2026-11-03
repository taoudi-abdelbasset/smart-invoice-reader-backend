# from pydantic import BaseModel, Field
# from models.contact import Contact

# class BusinessEntity(BaseModel):
#     first_name: str
#     last_name: str
#     addr: str
#     contact_list: list[Contact]

import uuid
from app.db.database import Base
from sqlalchemy import Column, Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class BusinessEntity(Base):
    __tablename__ = "business_entities"

    id = Column(Uuid(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    first_name = Column(String)
    last_name = Column(String)
    address = Column(String)
    country = Column(String, nullable=True)

    created_at= Column(DateTime(timezone=True), server_default=func.now())
    deleted_at= Column(DateTime(timezone=True))

    contacts = relationship("EntityContact", back_populates="entity")
    user = relationship("User", back_populates="business_entities")