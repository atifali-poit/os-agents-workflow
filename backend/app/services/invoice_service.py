from sqlalchemy.orm import Session, joinedload

from app.models import AuditLog, Invoice
from app.schemas import InvoiceCreate


def list_invoices(db: Session) -> list[Invoice]:
    return db.query(Invoice).options(joinedload(Invoice.vendor)).order_by(Invoice.id).all()


def create_invoice(db: Session, invoice_in: InvoiceCreate) -> Invoice:
    invoice = Invoice(**invoice_in.model_dump())
    db.add(invoice)
    db.flush()
    db.add(AuditLog(entity_type="invoice", entity_id=invoice.id, action="created", status="success", message=f"Invoice {invoice.invoice_number} created.", triggered_by="invoice_screen"))
    db.commit()
    db.refresh(invoice)
    return invoice
