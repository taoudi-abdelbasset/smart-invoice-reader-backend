from typing import Literal
from pydantic import BaseModel, Field


class ContactInput(BaseModel):
    type: Literal["email", "phone"]
    value: str = Field(description="Email address or phone number as printed")
    country: str | None = Field(None, description="Country code for phones, e.g. MA, FR")


class BusinessEntityInput(BaseModel):
    kind: Literal["company", "person"] = Field(description="company or an individual person")
    name: str | None = Field(None, description="Company name (kind=company)")
    first_name: str | None = Field(None, description="Person first name (kind=person)")
    last_name: str | None = Field(None, description="Person last name (kind=person)")
    address: str | None = None
    country: str | None = None
    contacts: list[ContactInput] = Field(default_factory=list, description="All emails and phones printed for this party")


class InvoiceItemInput(BaseModel):
    item_name: str
    qte: float = Field(1, description="Quantity")
    unit_price: float = Field(0, description="Unit price, plain number")
    tax_rate: float = Field(0, description="Tax rate in percent, e.g. 20")