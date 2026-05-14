from fastapi import APIRouter, Depends
from sqlalchemy import distinct, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, Employee, Invoice, PendingApproval, Rule, Vendor
from app.schemas import DashboardMetrics, DashboardRuleActivity

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
def dashboard_metrics(db: Session = Depends(get_db)):
    return {
        "total_invoices": db.query(Invoice).count(),
        "total_vendors": db.query(Vendor).count(),
        "total_employees": db.query(Employee).count(),
        "pending_approvals": db.query(PendingApproval).filter(PendingApproval.status == "pending").count(),
        "escalated_invoices": db.query(Invoice).filter(Invoice.status == "escalated").count(),
        "active_rules": db.query(Rule).filter(Rule.enabled.is_(True)).count(),
        "audit_logs": db.query(AuditLog).count(),
        "agent_activity": db.query(distinct(AuditLog.triggered_by)).count(),
    }


@router.get("/rule-activity", response_model=list[DashboardRuleActivity])
def dashboard_rule_activity(db: Session = Depends(get_db)):
    rules = db.query(Rule).order_by(Rule.id).all()
    rows = []
    for rule in rules:
        executions = (
            db.query(AuditLog)
            .filter(
                or_(
                    AuditLog.message.like(f"{rule.name} required%"),
                    AuditLog.message.like(f"{rule.name} executed%"),
                )
            )
            .count()
        )
        rows.append({"name": rule.name.replace("_", " "), "executions": executions})
    return rows
