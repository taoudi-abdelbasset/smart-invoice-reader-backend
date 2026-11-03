import uuid
from app.db.database import Base
from sqlalchemy import Column, Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Company(Base):
    __tablename__ = "companies"

    id = Column(Uuid(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    name = Column(String)
    address = Column(String)
    country = Column(String, nullable=True)

    created_at= Column(DateTime(timezone=True), server_default=func.now())
    deleted_at= Column(DateTime(timezone=True))

    contacts = relationship("CompanyContact", back_populates="company")
    user = relationship("User", back_populates="companies")