from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, aliased, joinedload, selectinload

from app.models.company import Company
from app.models.business_entity import BusinessEntity
from app.models.conversation import Conversation
from app.models.file import File
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.schemas.invoice import InvoiceCreate
from sqlalchemy.orm import contains_eager


def _load_options():
    return [
        selectinload(Invoice.items),
        joinedload(Invoice.file),
        joinedload(Invoice.issuer_company).selectinload(Company.contacts),
        joinedload(Invoice.buyer_company).selectinload(Company.contacts),
        joinedload(Invoice.issuer),
        joinedload(Invoice.buyer),
    ]


def create_invoice(db: Session, user_id: UUID, file_id: UUID, data: InvoiceCreate):
    file = db.query(File).get(file_id)
    if not file:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")

    if file.is_proccesed is True or db.query(Invoice).filter(Invoice.file_ref_id == file.id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "This file already has an invoice")

    duplicate = (
        db.query(Invoice)
        .filter(
            Invoice.user_id == user_id,
            Invoice.invoice_number == data.invoice_number,
            Invoice.deleted_at.is_(None),
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status.HTTP_409_CONFLICT, "Invoice number already exists")

    invoice = Invoice(
        user_id=user_id,
        file_ref_id=file_id,
        **data.model_dump(exclude={"file_id", "items"}),
    )
    invoice.items = [InvoiceItem(**item.model_dump()) for item in data.items]
    file.is_proccesed = True

    db.add(invoice)
    db.commit()
    return get_invoice(db, user_id, invoice.id)

def get_invoice_by_id(db: Session, invoice_id: UUID):
    return (
        db.query(Invoice)
        .options(*_load_options())
        .filter(
            Invoice.id == invoice_id,
            Invoice.deleted_at.is_(None),
        )
        .first()
    )

def get_invoice(db: Session, user_id: UUID, invoice_id: UUID):
    return (
        db.query(Invoice)
        .options(*_load_options())
        .filter(
            Invoice.id == invoice_id,
            Invoice.user_id == user_id,
            Invoice.deleted_at.is_(None),
        )
        .first()
    )

def get_user_invoice_list(db: Session, user_id: UUID):
    return (
        db.query(Invoice)
        .options(*_load_options())
        .filter(
            Invoice.user_id == user_id,
            Invoice.deleted_at.is_(None),
        )
        .order_by(Invoice.created_at.desc())
        .all()
    )

def get_session_invoice_list(db: Session, user_id: UUID, session_id: UUID):
    return (
        db.query(Invoice)
        .join(Invoice.file)
        .options(
            contains_eager(Invoice.file),
            selectinload(Invoice.items),
            joinedload(Invoice.issuer_company).selectinload(Company.contacts),
            joinedload(Invoice.buyer_company).selectinload(Company.contacts),
            joinedload(Invoice.issuer),
            joinedload(Invoice.buyer),
        )
        .filter(
            File.conversation_id == session_id,
            Invoice.user_id == user_id,
            Invoice.deleted_at.is_(None),
        )
        .order_by(Invoice.created_at.desc())
        .all()
    )

def search_invoices(
    db: Session,
    user_id: UUID,
    q: str | None = None,
    vendor: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    min_total: Decimal | None = None,
    max_total: Decimal | None = None,
    limit: int = 50,
    offset: int = 0,
):
    issuer = aliased(Company)

    query = (
        db.query(Invoice)
        .options(*_load_options())
        .filter(Invoice.user_id == user_id, Invoice.deleted_at.is_(None))
    )

    if q:
        query = query.filter(Invoice.invoice_number.ilike(f"%{q}%"))
    if vendor:
        query = query.filter(issuer.name.ilike(f"%{vendor}%"))
    if date_from:
        query = query.filter(Invoice.invoice_date >= date_from)
    if date_to:
        query = query.filter(Invoice.invoice_date <= date_to)
    if min_total is not None:
        query = query.filter(Invoice.total_amount >= min_total)
    if max_total is not None:
        query = query.filter(Invoice.total_amount <= max_total)

    return (
        query.order_by(Invoice.invoice_date.desc().nullslast(), Invoice.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

def get_user_companies_list(db: Session, user_id: UUID):
    return (
        db.query(Company)
        .options(selectinload(Company.contacts))
        .filter(
            Company.user_id == user_id,
            Company.deleted_at.is_(None),
        )
        .order_by(Company.created_at.desc())
        .all()
    )

def get_user_business_entity_list(db: Session, user_id: UUID):
    return (
        db.query(BusinessEntity)
        .options(selectinload(BusinessEntity.contacts))
        .filter(
            BusinessEntity.user_id == user_id,
            BusinessEntity.deleted_at.is_(None),
        )
        .order_by(BusinessEntity.created_at.desc())
        .all()
    )