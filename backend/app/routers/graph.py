from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PendingApprovalsGraph
from app.services.graph_service import GraphService

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/pending-approvals/{employee_id}", response_model=PendingApprovalsGraph)
def pending_approvals(employee_id: int, db: Session = Depends(get_db)):
    return GraphService(db).pending_approvals_for_employee(employee_id)


@router.get("/pending/{employee_id}", response_model=PendingApprovalsGraph)
def pending(employee_id: int, db: Session = Depends(get_db)):
    return GraphService(db).pending_approvals_for_employee(employee_id)
