from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import AuditLog, LeaveRequest
from app.schemas import LeaveRequestCreate, LeaveRequestOut, LeaveRequestUpdate
from app.services.runtime_engine import RuntimeEngine

router = APIRouter(prefix="/api/leave-requests", tags=["leave requests"])


@router.get("", response_model=list[LeaveRequestOut])
def list_leave_requests(db: Session = Depends(get_db)):
    return db.query(LeaveRequest).options(joinedload(LeaveRequest.employee)).order_by(LeaveRequest.id).all()


@router.post("", response_model=LeaveRequestOut)
def create_leave_request(leave_in: LeaveRequestCreate, db: Session = Depends(get_db)):
    leave = LeaveRequest(**leave_in.model_dump())
    db.add(leave)
    db.flush()
    db.add(AuditLog(entity_type="leave", entity_id=leave.id, action="submitted", status="success", message=f"Leave request #{leave.id} submitted for {leave.days} days.", triggered_by="leave_screen"))
    db.commit()
    db.refresh(leave)
    RuntimeEngine(db).execute("leave", triggered_by="hr_agent")
    db.refresh(leave)
    return leave


@router.put("/{leave_id}", response_model=LeaveRequestOut)
def update_leave_request(leave_id: int, leave_in: LeaveRequestUpdate, db: Session = Depends(get_db)):
    leave = db.get(LeaveRequest, leave_id)
    if leave is None:
        raise HTTPException(status_code=404, detail="Leave request not found")
    for key, value in leave_in.model_dump().items():
        setattr(leave, key, value)
    db.add(AuditLog(entity_type="leave", entity_id=leave.id, action="updated", status="success", message=f"Leave request #{leave.id} updated.", triggered_by="leave_screen"))
    db.commit()
    db.refresh(leave)
    return leave


@router.delete("/{leave_id}")
def delete_leave_request(leave_id: int, db: Session = Depends(get_db)):
    leave = db.get(LeaveRequest, leave_id)
    if leave is None:
        raise HTTPException(status_code=404, detail="Leave request not found")
    db.add(AuditLog(entity_type="leave", entity_id=leave.id, action="deleted", status="success", message=f"Leave request #{leave.id} deleted.", triggered_by="leave_screen"))
    db.delete(leave)
    db.commit()
    return {"deleted": True}
