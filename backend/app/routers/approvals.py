from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AgentApprovalsOut, ApprovalOut
from app.models import PendingApproval
from app.services.approval_service import complete_pending_approval, list_pending_agent_approvals, pending_approval_to_dict

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


@router.get("/agents", response_model=AgentApprovalsOut)
def agent_approvals(db: Session = Depends(get_db)):
    return list_pending_agent_approvals(db)


@router.get("", response_model=list[ApprovalOut])
def all_pending_approvals(db: Session = Depends(get_db)):
    approvals = db.query(PendingApproval).order_by(PendingApproval.created_at.desc()).all()
    return [pending_approval_to_dict(db, approval) for approval in approvals]


@router.post("/{approval_id}/approve", response_model=ApprovalOut)
def approve_pending_approval(approval_id: int, db: Session = Depends(get_db)):
    try:
        approval = complete_pending_approval(db, approval_id, "approved")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return pending_approval_to_dict(db, approval)


@router.post("/{approval_id}/reject", response_model=ApprovalOut)
def reject_pending_approval(approval_id: int, db: Session = Depends(get_db)):
    try:
        approval = complete_pending_approval(db, approval_id, "rejected")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return pending_approval_to_dict(db, approval)
