from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, Invoice, Vendor
from app.schemas import VendorCreate, VendorOut, VendorUpdate
from app.services.runtime_engine import RuntimeEngine

router = APIRouter(prefix="/api/vendors", tags=["vendors"])


@router.get("", response_model=list[VendorOut])
def list_vendors(db: Session = Depends(get_db)):
    return db.query(Vendor).order_by(Vendor.id).all()


@router.post("", response_model=VendorOut)
def create_vendor(vendor_in: VendorCreate, db: Session = Depends(get_db)):
    vendor = Vendor(**vendor_in.model_dump())
    db.add(vendor)
    db.flush()
    db.add(AuditLog(entity_type="vendor", entity_id=vendor.id, action="created", status="success", message=f"Vendor {vendor.name} created.", triggered_by="vendor_screen"))
    db.commit()
    db.refresh(vendor)
    RuntimeEngine(db).execute("vendor", triggered_by="procurement_agent")
    db.refresh(vendor)
    return vendor


@router.put("/{vendor_id}", response_model=VendorOut)
def update_vendor(vendor_id: int, vendor_in: VendorUpdate, db: Session = Depends(get_db)):
    vendor = db.get(Vendor, vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    for key, value in vendor_in.model_dump().items():
        setattr(vendor, key, value)
    db.add(AuditLog(entity_type="vendor", entity_id=vendor.id, action="updated", status="success", message=f"Vendor {vendor.name} updated.", triggered_by="vendor_screen"))
    db.commit()
    db.refresh(vendor)
    return vendor


@router.delete("/{vendor_id}")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.get(Vendor, vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    db.query(Invoice).filter(Invoice.vendor_id == vendor.id).delete()
    db.add(AuditLog(entity_type="vendor", entity_id=vendor.id, action="deleted", status="success", message=f"Vendor {vendor.name} deleted.", triggered_by="vendor_screen"))
    db.delete(vendor)
    db.commit()
    return {"deleted": True}
