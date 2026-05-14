from datetime import datetime, timedelta

from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models import ApprovalRequest, AuditLog, Employee, Invoice, LeaveRequest, PendingApproval, Vendor


ROLE_TO_POSITION = {
    "finance_director": "Finance Director",
    "finance_manager": "Finance Manager",
    "cfo": "CFO",
    "procurement_officer": "Procurement Officer",
    "procurement_approval": "Procurement Officer",
    "procurement_director": "Procurement Director",
    "procurement_analyst": "Procurement Analyst",
    "hr_manager": "HR Manager",
    "hr_director": "HR Director",
    "executive_committee": "Executive Committee",
}


def pending_approval_to_dict(db: Session, approval: PendingApproval) -> dict:
    position = ROLE_TO_POSITION.get(approval.required_role, approval.required_role.replace("_", " ").title())
    approver = db.query(Employee).filter(Employee.position == position).first()
    department = approver.department.name if approver and approver.department else "Operations"

    if approval.entity_type == "invoice":
        invoice = db.get(Invoice, approval.entity_id)
        title = f"Invoice {invoice.invoice_number}" if invoice else "Invoice"
        summary = f"Amount: ${invoice.amount:,.0f}" if invoice else f"{approval.required_role} approval required"
    elif approval.entity_type == "vendor":
        vendor = db.get(Vendor, approval.entity_id)
        title = f"Vendor {vendor.name}" if vendor else "Vendor"
        summary = f"{vendor.risk_level.title()} risk in {vendor.country}" if vendor else f"{approval.required_role} approval required"
    else:
        leave = db.get(LeaveRequest, approval.entity_id)
        title = f"Leave request #{approval.entity_id}"
        summary = f"{leave.days} days for {leave.employee.name} ({leave.reason})" if leave and leave.employee else f"{approval.required_role} approval required"

    return {
        "id": approval.id,
        "workflow_name": "RuleBasedWorkflow",
        "workflow_id": approval.workflow_id,
        "workflow_run_id": approval.workflow_id,
        "entity_type": approval.entity_type,
        "entity_id": approval.entity_id,
        "approval_key": approval.required_role,
        "flags": approval.flags,
        "approver_employee_id": approver.id if approver else None,
        "approver_name": approver.name if approver else position,
        "approver_role": position,
        "department": department,
        "status": approval.status,
        "pending_since": approval.created_at,
        "duration_pending_days": max((datetime.utcnow() - approval.created_at).days, 0),
        "title": title,
        "summary": summary,
        "related_count": 0,
        "timeline": [
            {"label": f"Rule matched {approval.entity_type}", "state": "complete", "complete": True},
            {"label": f"{position} approval", "state": "current", "complete": False},
            {"label": "Complete workflow", "state": "pending", "complete": False},
        ],
    }


def list_pending_agent_approvals(db: Session) -> dict[str, list[dict]]:
    approvals = (
        db.query(PendingApproval)
        .filter(PendingApproval.status == "pending")
        .order_by(PendingApproval.created_at)
        .all()
    )
    grouped = {"finance": [], "procurement": [], "hr": []}
    for approval in approvals:
        row = pending_approval_to_dict(db, approval)
        if approval.required_role == "finance_director":
            grouped["finance"].append(row)
        elif approval.required_role in {"finance_manager", "cfo"}:
            grouped["finance"].append(row)
        elif approval.required_role in {"procurement_officer", "procurement_approval", "procurement_director", "procurement_analyst"}:
            grouped["procurement"].append(row)
        elif approval.required_role in {"hr_manager", "hr_director", "executive_committee"}:
            grouped["hr"].append(row)
    return grouped


def complete_pending_approval(db: Session, approval_id: int, action: str) -> PendingApproval:
    approval = db.get(PendingApproval, approval_id)
    if approval is None:
        raise ValueError("Pending approval not found")
    if action not in {"approved", "rejected"}:
        raise ValueError("Action must be approved or rejected")
    if approval.status != "pending":
        raise ValueError("Pending approval has already been completed")

    approval.status = action
    approval.approved_at = datetime.utcnow()

    if approval.entity_type == "invoice":
        invoice = db.get(Invoice, approval.entity_id)
        if invoice is not None:
            invoice.requires_approval = False
            invoice.status = "approved" if action == "approved" else "rejected"
    elif approval.entity_type == "vendor":
        vendor = db.get(Vendor, approval.entity_id)
        if vendor is not None:
            vendor.status = "active" if action == "approved" else "blocked"
    elif approval.entity_type == "leave":
        leave = db.get(LeaveRequest, approval.entity_id)
        if leave is not None:
            leave.status = action

    db.add(
        AuditLog(
            entity_type=approval.entity_type,
            entity_id=approval.entity_id,
            action=f"{action}_approval",
            status=action,
            message=f"{approval.required_role} approval was {action}; workflow_id={approval.workflow_id}.",
            triggered_by="approval_console",
            workflow_id=approval.workflow_id,
        )
    )
    db.commit()
    db.refresh(approval)
    return approval


def approval_to_dict(db: Session, approval: ApprovalRequest) -> dict:
    approver = approval.approver
    department = approver.department.name if approver.department else "Operations"
    related_count = 0

    if approval.entity_type == "invoice":
        invoice = db.get(Invoice, approval.entity_id)
        vendor = invoice.vendor if invoice else None
        title = f"Invoice #{invoice.invoice_number}" if invoice else "Invoice"
        summary = f"Amount: ${invoice.amount:,.0f}" if invoice else approval.details
        if vendor and approval.approval_key == "procurement_officer":
            related_count = db.query(Invoice).filter(Invoice.vendor_id == vendor.id).count()
            summary = f'Vendor "{vendor.name}" ({vendor.risk_level.title()} Risk)'
    elif approval.entity_type == "vendor":
        vendor = db.get(Vendor, approval.entity_id)
        title = f'Vendor "{vendor.name}"' if vendor else "Vendor"
        summary = f"{vendor.risk_level.title()} risk validation" if vendor else approval.details
        related_count = db.query(Invoice).filter(Invoice.vendor_id == approval.entity_id).count()
    else:
        leave = db.get(LeaveRequest, approval.entity_id)
        title = f"Leave request - {leave.employee.name}" if leave and leave.employee else "Leave request"
        summary = f"{leave.days} days" if leave else approval.details

    return {
        "id": approval.id,
        "workflow_name": approval.workflow_name,
        "workflow_id": approval.workflow_id,
        "workflow_run_id": approval.workflow_run_id,
        "entity_type": approval.entity_type,
        "entity_id": approval.entity_id,
        "approval_key": approval.approval_key,
        "approver_employee_id": approval.approver_employee_id,
        "approver_name": approver.name,
        "approver_role": approver.position,
        "department": department,
        "status": approval.status,
        "pending_since": approval.pending_since,
        "duration_pending_days": max((datetime.utcnow() - approval.pending_since).days, 0),
        "title": title,
        "summary": summary,
        "related_count": related_count,
        "timeline": timeline_for_approval(approval),
    }


def list_agent_approvals(db: Session) -> dict[str, list[dict]]:
    approvals = (
        db.query(ApprovalRequest)
        .options(joinedload(ApprovalRequest.approver).joinedload(Employee.department))
        .filter(ApprovalRequest.status == "pending")
        .order_by(ApprovalRequest.pending_since)
        .all()
    )
    grouped = {"finance": [], "procurement": [], "hr": []}
    for approval in approvals:
        row = approval_to_dict(db, approval)
        if approval.approval_key == "finance_director":
            grouped["finance"].append(row)
        elif approval.approval_key in {"procurement_officer", "procurement_approval"}:
            grouped["procurement"].append(row)
        elif approval.approval_key == "hr_manager":
            grouped["hr"].append(row)
    return grouped


def complete_approval(db: Session, approval_id: int, action: str, *, signal_temporal: bool = True) -> ApprovalRequest:
    approval = db.get(ApprovalRequest, approval_id)
    if approval is None:
        raise ValueError("Approval request not found")
    if action not in {"approved", "rejected"}:
        raise ValueError("Action must be approved or rejected")

    approval.status = action
    approval.completed_at = datetime.utcnow()
    remaining_approvals = (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.workflow_id == approval.workflow_id,
            ApprovalRequest.id != approval.id,
            ApprovalRequest.status == "pending",
        )
        .count()
    )
    if approval.entity_type == "invoice":
        invoice = db.get(Invoice, approval.entity_id)
        if invoice is not None:
            if action == "rejected":
                invoice.status = "rejected"
                invoice.requires_approval = False
            elif remaining_approvals == 0:
                invoice.status = "approved"
                invoice.requires_approval = False
            else:
                invoice.status = "escalated"
                invoice.requires_approval = True
    elif approval.entity_type == "vendor":
        vendor_invoices = db.query(Invoice).filter(Invoice.vendor_id == approval.entity_id).all()
        for invoice in vendor_invoices:
            invoice.requires_approval = action == "rejected"
    elif approval.entity_type == "leave_request":
        leave = db.get(LeaveRequest, approval.entity_id)
        if leave is not None:
            leave.status = action

    db.add(
        AuditLog(
            entity_type=approval.entity_type,
            entity_id=approval.entity_id,
            action=f"{action}_approval",
            status=action,
            message=f"{approval.workflow_name} {approval.approval_key} was {action}; workflow_id={approval.workflow_id}.",
            triggered_by="approval_console",
            workflow_id=approval.workflow_id,
        )
    )
    db.commit()
    db.refresh(approval)
    if signal_temporal:
        signal_temporal_approval(approval.workflow_id, approval.approval_key, action == "approved")
    return approval


def signal_temporal_approval(workflow_id: str, approval_key: str, approved: bool) -> None:
    if not settings.temporal_enabled:
        return

    import asyncio

    from temporalio.client import Client

    from app.temporal.workflows import ApprovalDecision

    async def signal() -> None:
        client = await Client.connect(settings.temporal_address, namespace=settings.temporal_namespace)
        handle = client.get_workflow_handle(workflow_id)
        await handle.signal("approve", ApprovalDecision(key=approval_key, approved=approved))

    try:
        asyncio.run(signal())
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(signal())
        except Exception:
            return
    except Exception:
        return


def ensure_seed_approval(
    db: Session,
    *,
    workflow_name: str,
    workflow_id: str,
    workflow_run_id: str,
    entity_type: str,
    entity_id: int,
    approval_key: str,
    approver_employee_id: int,
    details: str,
    days_pending: int = 0,
) -> ApprovalRequest:
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.workflow_run_id == workflow_run_id).one_or_none()
    if approval is not None:
        return approval

    approval = ApprovalRequest(
        workflow_name=workflow_name,
        workflow_id=workflow_id,
        workflow_run_id=workflow_run_id,
        entity_type=entity_type,
        entity_id=entity_id,
        approval_key=approval_key,
        approver_employee_id=approver_employee_id,
        details=details,
        pending_since=datetime.utcnow() - timedelta(days=days_pending),
    )
    db.add(approval)
    return approval


def timeline_for_approval(approval: ApprovalRequest) -> list[dict[str, str | bool]]:
    if approval.workflow_name == "HighValueInvoiceWorkflow":
        steps = [
            ("Validate invoice exists", "complete"),
            ("Check vendor risk level", "complete"),
            ("Finance director approval", "current" if approval.approval_key == "finance_director" else "complete"),
            ("Procurement officer approval", "current" if approval.approval_key == "procurement_officer" else "pending"),
            ("Complete payment processing", "pending"),
        ]
    elif approval.workflow_name == "VendorRiskValidationWorkflow":
        steps = [
            ("Validate vendor", "complete"),
            ("Procurement approval", "current"),
            ("Complete validation", "pending"),
        ]
    else:
        steps = [
            ("Validate leave request", "complete"),
            ("HR manager approval", "current"),
            ("Complete", "pending"),
        ]
    return [{"label": label, "state": state, "complete": state == "complete"} for label, state in steps]
