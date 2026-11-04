from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.invoice import InvoiceOut
from app.services import auth_serivce, invoice_service

router = APIRouter(prefix="/invoice",tags=["invoice"])

@router.get("/", response_model=list[InvoiceOut])
def get_invoice_list(
    user_id:UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db)
):
    return invoice_service.get_user_invoice_list(db=db,user_id=user_id)

@router.get("/session/{session_id}", response_model=list[InvoiceOut])
def get_invoice_list(
    session_id: UUID,
    user_id:UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db)
):
    return invoice_service.get_session_invoice_list(db,user_id,session_id)

@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice_list(
    invoice_id: UUID,
    user_id:UUID = Depends(auth_serivce.current_user_id),
    db: Session = Depends(get_db)
):
    return invoice_service.get_invoice(db,user_id,invoice_id)