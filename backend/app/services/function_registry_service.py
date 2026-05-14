import re
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.models import FunctionRegistry, Invoice
from app.models.entities import Employee
from app.services.approval_service import ensure_seed_approval
from app.services.audit_service import create_audit_log


def parse_action(action_name: str) -> tuple[str, str | None]:
    match = re.fullmatch(r"([a-z_]+)(?:\(([^)]*)\))?", action_name.strip())
    if not match:
        raise ValueError(f"Invalid action expression: {action_name}")
    function_name = match.group(1)
    argument = match.group(2).strip().strip('"').strip("'") if match.group(2) else None
    return function_name, argument


def ensure_registered(db: Session, function_name: str) -> FunctionRegistry:
    function = (
        db.query(FunctionRegistry)
        .filter(FunctionRegistry.name == function_name, FunctionRegistry.is_active.is_(True))
        .first()
    )
    if not function:
        raise PermissionError(f"Function {function_name} is not active in the registry.")
    return function


def execute_registered_function(
    db: Session,
    *,
    action_expression: str,
    entity_type: str,
    entity: object,
    triggered_by: str,
) -> str:
    function_name, argument = parse_action(action_expression)
    ensure_registered(db, function_name)
    functions: dict[str, Callable[[Session, object, str | None, str], str]] = {
        "require_approval": require_approval,
        "notify": notify,
        "escalate": escalate,
        "approve_invoice": approve_invoice,
        "reject_invoice": reject_invoice,
    }
    return functions[function_name](db, entity, argument, triggered_by)


def require_approval(db: Session, entity: object, role: str | None, triggered_by: str) -> str:

    if isinstance(entity, Invoice):
        entity.requires_approval = True
        entity.status = "escalated"
        message = f"{role or 'configured role'} approval required"

        # Map role to approval_key and position
        role_to_approval_key = {
            "finance_director": "finance_director",
            "procurement_officer": "procurement_officer",
            "hr_manager": "hr_manager",
        }
        role_to_position = {
            "finance_director": "Finance Director",
            "procurement_officer": "Procurement Officer",
            "hr_manager": "HR Manager",
        }
        approval_key = role_to_approval_key.get(role or "")
        position = role_to_position.get(role or "")
        if not approval_key or not position:
            # Skip if not mapped
            return message

        # Find employee by position
        approver = db.query(Employee).filter(Employee.position == position).first()
        if approver:
            ensure_seed_approval(
                db,
                workflow_name="RuleBasedWorkflow",
                workflow_id=f"rule-{entity.id}-{approval_key}",
                workflow_run_id=f"rule-{entity.id}-{approval_key}-{approver.id}",
                entity_type="invoice",
                entity_id=entity.id,
                approval_key=approval_key,
                approver_employee_id=approver.id,
                details=f"Rule triggered approval for {entity.invoice_number}",
                days_pending=0,
            )

        create_audit_log(
            db,
            entity_type="invoice",
            entity_id=entity.id,
            action="require_approval",
            status="success",
            message=message,
            triggered_by=triggered_by,
        )
        create_audit_log(
            db,
            entity_type="notification",
            entity_id=entity.id,
            action="notify",
            status="success",
            message=f"Notification queued for {role or 'approval role'}",
            triggered_by=triggered_by,
        )
        return message
    create_audit_log(
        db,
        entity_type="simulation",
        entity_id=0,
        action="require_approval",
        status="success",
        message=f"Simulated approval requirement for {role}",
        triggered_by=triggered_by,
    )
    return f"Simulated approval requirement for {role}"


def notify(db: Session, entity: object, team: str | None, triggered_by: str) -> str:
    entity_id = getattr(entity, "id", 0)
    create_audit_log(
        db,
        entity_type="notification",
        entity_id=entity_id,
        action="notify",
        status="success",
        message=f"Notification sent to {team or 'team'}",
        triggered_by=triggered_by,
    )
    return f"Notification sent to {team or 'team'}"


def escalate(db: Session, entity: object, team: str | None, triggered_by: str) -> str:
    if isinstance(entity, Invoice):
        entity.status = "escalated"
    entity_id = getattr(entity, "id", 0)
    create_audit_log(
        db,
        entity_type="invoice" if isinstance(entity, Invoice) else "simulation",
        entity_id=entity_id,
        action="escalate",
        status="success",
        message=f"Escalated to {team or 'configured team'}",
        triggered_by=triggered_by,
    )
    return f"Escalated to {team or 'configured team'}"


def approve_invoice(db: Session, entity: object, _: str | None, triggered_by: str) -> str:
    if not isinstance(entity, Invoice):
        raise ValueError("approve_invoice can only run for invoices.")
    entity.status = "approved"
    create_audit_log(
        db,
        entity_type="invoice",
        entity_id=entity.id,
        action="approve_invoice",
        status="success",
        message="Invoice approved",
        triggered_by=triggered_by,
    )
    return "Invoice approved"


def reject_invoice(db: Session, entity: object, _: str | None, triggered_by: str) -> str:
    if not isinstance(entity, Invoice):
        raise ValueError("reject_invoice can only run for invoices.")
    entity.status = "rejected"
    create_audit_log(
        db,
        entity_type="invoice",
        entity_id=entity.id,
        action="reject_invoice",
        status="success",
        message="Invoice rejected",
        triggered_by=triggered_by,
    )
    return "Invoice rejected"

