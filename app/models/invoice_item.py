import uuid
from app.db.database import Base
from sqlalchemy import Column, Uuid, String, DateTime, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Uuid(as_uuid=True),primary_key=True,default=uuid.uuid4)
    invoice_id = Column(Uuid(as_uuid=True),ForeignKey("invoices.id"),nullable=False)
    
    index = Column(Integer, nullable=True)
    item_name = Column(String)

    qte = Column(Float, default=1)
    unit_price = Column(Float,default=0)
    tax_rate = Column(Float,default=0)


    created_at= Column(DateTime(timezone=True), server_default=func.now())
    deleted_at= Column(DateTime(timezone=True))

    invoice = relationship("Invoice", back_populates="items")