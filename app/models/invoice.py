import uuid
from enum import Enum as EnumClass
from app.db.database import Base
from sqlalchemy import Column, Uuid, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Uuid(as_uuid=True),primary_key=True,default=uuid.uuid4)

    user_id = Column(Uuid(as_uuid=True),ForeignKey("users.id"),nullable=False)
    file_ref_id = Column(Uuid(as_uuid=True),ForeignKey("files.id"),nullable=False, unique=True)
    
    invoice_number = Column(String)

    invoice_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))

    note = Column(String, nullable=True)
    currency = Column(String(3))
    subtotal = Column(Integer)
    tax_amount = Column(Integer)
    total_amount = Column(Integer)
    payment_method = Column(String, nullable=True)
    
    items = relationship("InvoiceItem", back_populates="invoice")

    issuer_company_id = Column(Uuid(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    issuer_id = Column(Uuid(as_uuid=True), ForeignKey("business_entities.id"), nullable=True)
    # issuer_details: BusinessEntity | None
    
    buyer_company_id = Column(Uuid(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    buyer_id = Column(Uuid(as_uuid=True), ForeignKey("business_entities.id"), nullable=True)

    created_at= Column(DateTime(timezone=True), server_default=func.now())
    deleted_at= Column(DateTime(timezone=True))

    user = relationship("User", back_populates="invoices")
    file = relationship("File", back_populates="invoice")

    issuer_company = relationship("Company", foreign_keys=[issuer_company_id])
    issuer = relationship("BusinessEntity", foreign_keys=[issuer_id])

    buyer_company = relationship("Company", foreign_keys=[buyer_company_id])
    buyer = relationship("BusinessEntity", foreign_keys=[buyer_id])
