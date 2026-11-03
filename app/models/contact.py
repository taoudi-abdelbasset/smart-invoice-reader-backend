import enum
import uuid
from sqlalchemy import Column, Uuid, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class ContactType(str, enum.Enum):
    email = "email"
    phone = "phone"


class ContactMixin:
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(ContactType), nullable=False)
    value = Column(String, nullable=False)
    country = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True))


class CompanyContact(ContactMixin, Base):
    __tablename__ = "company_contacts"

    company_id = Column(Uuid(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="contacts")


class EntityContact(ContactMixin, Base):
    __tablename__ = "entity_contacts"

    entity_id = Column(Uuid(as_uuid=True), ForeignKey("business_entities.id"), nullable=False)
    entity = relationship("BusinessEntity", back_populates="contacts")