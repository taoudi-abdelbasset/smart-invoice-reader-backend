import json
from typing import List
from agno.tools import Toolkit
from agno.utils.log import logger
from app.services import invoice_service
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from app.models.invoice import Invoice
from datetime import datetime, timedelta
from app.models.file import File
from app.schemas.invoice import InvoiceCreate, InvoiceItemCreate
from app.schemas.invoice_tool import BusinessEntityInput, InvoiceItemInput

def _parse_date(value: str) -> datetime | None:
    """Tool input: 'YYYY-MM-DD' string -> datetime (None if empty)."""
    return datetime.fromisoformat(value) if value else None

def _format_date(value: datetime | None) -> str | None:
    """Tool output: datetime -> 'YYYY-MM-DD' string (None if empty)."""
    return value.date().isoformat() if value else None

def _summary(i: Invoice) -> dict:
    return {
        "id": str(i.id),
        "invoice_number": i.invoice_number,
        "invoice_date": _format_date(i.invoice_date),
        "due_date": _format_date(i.due_date),
        "created_at": _format_date(i.created_at),
        "vendor": i.issuer_company.name if i.issuer_company else None,
        "currency": i.currency,
        "total_amount": i.total_amount,
    }

def _to_json(invoices: list[Invoice]) -> str:
    return json.dumps([_summary(i) for i in invoices])

class InvoiceTools(Toolkit):
    def __init__(self, db: Session, user_id: UUID, session_id: UUID, **kwargs):
        self.db = db
        self.user_id = user_id
        self.session_id = session_id
        super().__init__(
            name="invoice_tools",
            tools=[
                self.list_my_invoices,
                self.search_my_invoices,
                self.list_my_session_invoice,
                self.save_invoice,

            ],
            **kwargs,
        )

    def list_my_invoices(self) -> str:
        """
        List all invoices saved by the current user.
        """
        return _to_json(invoice_service.get_user_invoice_list(self.db, self.user_id))

    def list_my_session_invoice(self):
        """
        List the invoices saved in the current conversation only.
        Use this when the user asks about invoices from this chat/conversation.
        To search across all conversations, use search_my_invoices instead.
        """
        return _to_json(
            invoice_service.get_session_invoice_list(self.db, self.user_id, self.session_id)
        )

    def search_my_invoices(
        self,
        query: str = "",
        vendor: str = "",
        date_from: str = "",
        date_to: str = "",
        min_total: float | None = None,
        max_total: float | None = None,
        limit: int = 20,
    ) -> str:
        """
        Search the current user's saved invoices. All filters are optional and combined with AND.
        Leave a filter empty to ignore it.

        Args:
            query: Text to match inside the invoice number (partial match, case-insensitive).
            vendor: Text to match in the vendor (issuer company) name (partial match, case-insensitive).
            date_from: Earliest invoice date, inclusive, format YYYY-MM-DD.
            date_to: Latest invoice date, inclusive, format YYYY-MM-DD.
            min_total: Minimum total_amount, inclusive.
            max_total: Maximum total_amount, inclusive.
            limit: Maximum number of invoices to return (default 20, max 50).

        Returns:
            JSON list of invoices with id, invoice_number, invoice_date, vendor, currency, total_amount.
        """
        try:
            start = _parse_date(date_from)
            end = _parse_date(date_to)
        except ValueError:
            return json.dumps({"error": "Dates must use the format YYYY-MM-DD."})
        if end:
            end += timedelta(days=1) - timedelta(microseconds=1)

        invoices = invoice_service.search_invoices(
            self.db,
            self.user_id,
            q=query or None,
            vendor=vendor or None,
            date_from=start,
            date_to=end,
            min_total=float(str(min_total)) if min_total is not None else None,
            max_total=float(str(max_total)) if max_total is not None else None,
            limit=min(limit, 50),
        )
        return json.dumps([_summary(i) for i in invoices])

    def save_invoice(
        self,
        file_id: str,
        invoice_number: str,
        issuer: BusinessEntityInput | None = None,
        buyer: BusinessEntityInput | None = None,
        items: list[InvoiceItemInput] | None = None,
        invoice_date: str = "",
        due_date: str = "",
        currency: str = "",
        subtotal: float | None = None,
        tax_amount: float | None = None,
        total_amount: float | None = None,
        payment_method: str = "",
        note: str = "",
    ) -> str:
        """
        Save the invoice extracted from the uploaded file. Call it once per file, only after
        the user confirmed the extracted data. Leave unknown fields empty or null, never guess.

        Args:
            file_id: Is the ID of the File uploaded.
            invoice_number: Invoice number exactly as printed.
            issuer: Who issued the invoice (the vendor): a company or a person, with address,
                tax id and ALL contacts (emails, phones) printed on the invoice.
            buyer: Who the invoice is addressed to, same structure as issuer.
            items: Every line item with item_name, qte, unit_price, tax_rate (percent).
            invoice_date: Format YYYY-MM-DD.
            due_date: Format YYYY-MM-DD.
            currency: ISO code (MAD, EUR, USD...).
            subtotal: Total before tax, plain number.
            tax_amount: Total tax, plain number.
            total_amount: Final total, plain number.
            payment_method: Payment method if printed.
            note: just additional note in the invoice it can be empty if not found in the invoice.

        Returns:
            JSON with the saved invoice id, or an error message.
        """
        try:
            file_uuid = UUID(file_id)
            issuer_company_id = issuer_id = buyer_company_id = buyer_id = None
            if issuer:
                issuer_company_id, issuer_id = invoice_service.get_or_create_party(self.db, self.user_id, issuer)
            if buyer:
                buyer_company_id, buyer_id = invoice_service.get_or_create_party(self.db, self.user_id, buyer)

            data = InvoiceCreate(
                file_id=file_uuid,
                invoice_number=invoice_number,
                invoice_date=_parse_date(invoice_date),
                due_date=_parse_date(due_date),
                currency=currency or None,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                payment_method=payment_method or None,
                note=note or None,
                issuer_company_id=issuer_company_id,
                issuer_id=issuer_id,
                buyer_company_id=buyer_company_id,
                buyer_id=buyer_id,
                items=[InvoiceItemCreate(index=n, **it.model_dump()) for n, it in enumerate(items or [], 1)],
            )
            invoice = invoice_service.create_invoice(self.db, self.user_id, self.session_id, file_uuid, data)
            return json.dumps({"saved": True, "invoice_id": str(invoice.id)})
        except HTTPException as e:
            self.db.rollback()
            return json.dumps({"error": e.detail})
        except ValueError as e:
            self.db.rollback()
            return json.dumps({"error": str(e)})