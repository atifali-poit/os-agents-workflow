from sqlalchemy.orm import Session

from app.models import AuditLog


def create_audit_log(
    db: Session,
    *,
    entity_type: str,
    entity_id: int,
    action: str,
    status: str,
    message: str,
    triggered_by: str,
) -> AuditLog:
    log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        status=status,
        message=message,
        triggered_by=triggered_by,
    )
    db.add(log)
    return log


def list_audit_logs(db: Session) -> list[AuditLog]:
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(200).all()

