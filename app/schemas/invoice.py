from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from app.models.contact import ContactType
from app.schemas.file import UploadedMiniFile


class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    type: ContactType
    value: str
    country: str | None = None
    created_at: datetime
    deleted_at: datetime | None = None


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    address: str | None = None
    country: str | None = None
    created_at: datetime
    deleted_at: datetime | None = None
    contacts: list[ContactOut] = []


class BusinessEntityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    first_name: str
    last_name: str
    address: str | None = None
    country: str | None = None
    created_at: datetime
    deleted_at: datetime | None = None
    contacts: list[ContactOut] = []


class InvoiceItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    index: int | None = None
    item_name: str
    qte: float
    unit_price: float
    tax_rate: float
    created_at: datetime
    deleted_at: datetime | None = None


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    invoice_number: str

    # in case the agent sets missing values to null
    invoice_date: datetime | None = None
    due_date: datetime | None = None
    note: str | None = None
    currency: str | None = None
    subtotal: float | None = None
    tax_amount: float | None = None
    total_amount: float | None = None
    payment_method: str | None = None

    items: list[InvoiceItemOut] = []

    issuer_company: CompanyOut | None = None
    issuer: BusinessEntityOut | None = None
    buyer_company: CompanyOut | None = None
    buyer: BusinessEntityOut | None = None

    created_at: datetime
    deleted_at: datetime | None = None

    file: UploadedMiniFile

class InvoiceItemCreate(BaseModel):
    index: int | None = None
    item_name: str
    qte: float
    unit_price: float
    tax_rate: float


class InvoiceCreate(BaseModel):
    file_id: UUID
    invoice_number: str

    invoice_date: datetime | None = None
    due_date: datetime | None = None
    note: str | None = None
    currency: str | None = None
    subtotal: float | None = None
    tax_amount: float | None = None
    total_amount: float | None = None
    payment_method: str | None = None

    issuer_company_id: UUID | None = None
    issuer_id: UUID | None = None
    buyer_company_id: UUID | None = None
    buyer_id: UUID | None = None

    items: list[InvoiceItemCreate] = []