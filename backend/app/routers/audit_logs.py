from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AuditLogOut
from app.services.audit_service import list_audit_logs

router = APIRouter(prefix="/api/audit-logs", tags=["audit logs"])


@router.get("", response_model=list[AuditLogOut])
def get_audit_logs(db: Session = Depends(get_db)):
    return list_audit_logs(db)

