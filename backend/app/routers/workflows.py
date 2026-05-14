from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ApprovalActionRequest,
    InvoiceWorkflowStartRequest,
    WorkflowApprovalResponse,
    WorkflowStartResponse,
    WorkflowStatusResponse,
)
from app.services.workflow_api_service import WorkflowAPIService

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.post("/invoice/start", response_model=WorkflowStartResponse)
def start_invoice_workflow(request: InvoiceWorkflowStartRequest, db: Session = Depends(get_db)):
    try:
        return WorkflowAPIService(db).start_invoice_workflow(request.invoice_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Invoice not found") from exc


@router.post("/{workflow_id}/approve", response_model=WorkflowApprovalResponse)
def approve_workflow(workflow_id: str, request: ApprovalActionRequest, db: Session = Depends(get_db)):
    if request.action not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="Action must be approved or rejected")
    return WorkflowAPIService(db).approve_workflow(workflow_id, request.action, request.approval_id)


@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse)
def workflow_status(workflow_id: str, db: Session = Depends(get_db)):
    return WorkflowAPIService(db).workflow_status(workflow_id)
