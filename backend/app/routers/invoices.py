from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, Invoice
from app.schemas import InvoiceCreate, InvoiceOut, InvoiceUpdate
from app.services.invoice_service import create_invoice, list_invoices
from app.services.runtime_engine import RuntimeEngine

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.get("", response_model=list[InvoiceOut])
def get_invoices(db: Session = Depends(get_db)):
    return list_invoices(db)


@router.post("", response_model=InvoiceOut)
def post_invoice(invoice_in: InvoiceCreate, db: Session = Depends(get_db)):
    invoice = create_invoice(db, invoice_in)
    RuntimeEngine(db).execute("invoice", triggered_by="finance_agent")
    db.refresh(invoice)
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceOut)
def put_invoice(invoice_id: int, invoice_in: InvoiceUpdate, db: Session = Depends(get_db)):
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    for key, value in invoice_in.model_dump().items():
        setattr(invoice, key, value)
    db.add(AuditLog(entity_type="invoice", entity_id=invoice.id, action="updated", status="success", message=f"Invoice {invoice.invoice_number} updated.", triggered_by="invoice_screen"))
    db.commit()
    db.refresh(invoice)
    return invoice


@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.add(AuditLog(entity_type="invoice", entity_id=invoice.id, action="deleted", status="success", message=f"Invoice {invoice.invoice_number} deleted.", triggered_by="invoice_screen"))
    db.delete(invoice)
    db.commit()
    return {"deleted": True}
