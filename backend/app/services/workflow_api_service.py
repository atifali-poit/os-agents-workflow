import asyncio
from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models import ApprovalRequest, AuditLog, Employee, Invoice
from app.services.approval_service import approval_to_dict, complete_approval, ensure_seed_approval


class WorkflowAPIService:
    def __init__(self, db: Session):
        self.db = db

    def start_invoice_workflow(self, invoice_id: int) -> dict:
        invoice = self.db.query(Invoice).options(joinedload(Invoice.vendor)).filter(Invoice.id == invoice_id).one()
        workflow_id = f"high-value-invoice-{invoice.id}"
        run_id = self._start_temporal_invoice_workflow(workflow_id, invoice)
        approvals = self._ensure_invoice_approvals(invoice, workflow_id)

        invoice.status = "escalated" if approvals else "approved"
        invoice.requires_approval = bool(approvals)
        self.db.add(
            AuditLog(
                entity_type="invoice",
                entity_id=invoice.id,
                action="workflow_started",
                status="pending" if approvals else "completed",
                message=f"HighValueInvoiceWorkflow started for {invoice.invoice_number}; workflow_id={workflow_id}.",
                triggered_by="workflow_api",
                workflow_id=workflow_id,
            )
        )
        self.db.commit()
        return {
            "workflow_id": workflow_id,
            "run_id": run_id,
            "status": "WAITING_APPROVAL" if approvals else "COMPLETED",
            "pending_approvals": [approval_to_dict(self.db, approval) for approval in approvals],
        }

    def approve_workflow(self, workflow_id: str, action: str, approval_id: int | None = None) -> dict:
        query = self.db.query(ApprovalRequest).filter(ApprovalRequest.workflow_id == workflow_id, ApprovalRequest.status == "pending")
        approval = query.filter(ApprovalRequest.id == approval_id).one_or_none() if approval_id else query.order_by(ApprovalRequest.id).first()
        if approval is None:
            return {
                "workflow_id": workflow_id,
                "status": "COMPLETED",
                "resumed": False,
                "pending_approvals": [],
            }

        complete_approval(self.db, approval.id, action, signal_temporal=True)
        pending = self._pending_approvals(workflow_id)
        status = "WAITING_APPROVAL" if pending else ("REJECTED" if action == "rejected" else "COMPLETED")
        if not pending:
            self.db.add(
                AuditLog(
                    entity_type=approval.entity_type,
                    entity_id=approval.entity_id,
                    action="workflow_resumed",
                    status=status.lower(),
                    message=f"{approval.workflow_name} resumed after approval signal; workflow_id={workflow_id}.",
                    triggered_by="workflow_api",
                    workflow_id=workflow_id,
                )
            )
            self.db.commit()
        return {
            "workflow_id": workflow_id,
            "status": status,
            "resumed": True,
            "pending_approvals": [approval_to_dict(self.db, item) for item in pending],
        }

    def workflow_status(self, workflow_id: str) -> dict:
        approvals = self._all_approvals(workflow_id)
        pending = [approval for approval in approvals if approval.status == "pending"]
        history_logs = (
            self.db.query(AuditLog)
            .filter(AuditLog.workflow_id == workflow_id)
            .order_by(AuditLog.timestamp)
            .all()
        )
        workflow_name = approvals[0].workflow_name if approvals else "HighValueInvoiceWorkflow"
        status = "WAITING_APPROVAL" if pending else "COMPLETED"
        current_step = self._current_step(pending, history_logs)
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "status": status,
            "current_step": current_step,
            "pending_approvals": [approval_to_dict(self.db, approval) for approval in pending],
            "history": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action,
                    "status": log.status,
                    "message": log.message,
                }
                for log in history_logs
            ],
        }

    def _ensure_invoice_approvals(self, invoice: Invoice, workflow_id: str) -> list[ApprovalRequest]:
        approvals: list[ApprovalRequest] = []
        if invoice.amount > 50000:
            approver = self._employee_by_position("Finance Director")
            approvals.append(
                ensure_seed_approval(
                    self.db,
                    workflow_name="HighValueInvoiceWorkflow",
                    workflow_id=workflow_id,
                    workflow_run_id=f"{workflow_id}-finance_director",
                    entity_type="invoice",
                    entity_id=invoice.id,
                    approval_key="finance_director",
                    approver_employee_id=approver.id,
                    details=f"{invoice.invoice_number} waiting for finance director approval",
                )
            )
        if invoice.vendor and invoice.vendor.risk_level == "high":
            approver = self._employee_by_position("Procurement Officer")
            approvals.append(
                ensure_seed_approval(
                    self.db,
                    workflow_name="HighValueInvoiceWorkflow",
                    workflow_id=workflow_id,
                    workflow_run_id=f"{workflow_id}-procurement_officer",
                    entity_type="invoice",
                    entity_id=invoice.id,
                    approval_key="procurement_officer",
                    approver_employee_id=approver.id,
                    details=f"{invoice.invoice_number} waiting for procurement officer approval",
                )
            )
        return approvals

    def _start_temporal_invoice_workflow(self, workflow_id: str, invoice: Invoice) -> str:
        if not settings.temporal_enabled:
            return f"{workflow_id}-local"

        async def start() -> str:
            from temporalio.client import Client

            client = await Client.connect(settings.temporal_address, namespace=settings.temporal_namespace)
            handle = await client.start_workflow(
                "HighValueInvoiceWorkflow",
                invoice.id,
                invoice.amount,
                invoice.vendor.risk_level if invoice.vendor else "low",
                id=workflow_id,
                task_queue=settings.temporal_task_queue,
            )
            return handle.run_id

        try:
            return asyncio.run(start())
        except Exception:
            return f"{workflow_id}-local"

    def _employee_by_position(self, position: str) -> Employee:
        return self.db.query(Employee).filter(Employee.position == position).one()

    def _pending_approvals(self, workflow_id: str) -> list[ApprovalRequest]:
        return (
            self.db.query(ApprovalRequest)
            .options(joinedload(ApprovalRequest.approver).joinedload(Employee.department))
            .filter(ApprovalRequest.workflow_id == workflow_id, ApprovalRequest.status == "pending")
            .order_by(ApprovalRequest.id)
            .all()
        )

    def _all_approvals(self, workflow_id: str) -> list[ApprovalRequest]:
        return (
            self.db.query(ApprovalRequest)
            .options(joinedload(ApprovalRequest.approver).joinedload(Employee.department))
            .filter(ApprovalRequest.workflow_id == workflow_id)
            .order_by(ApprovalRequest.id)
            .all()
        )

    def _current_step(self, pending: list[ApprovalRequest], history_logs: list[AuditLog]) -> str:
        if pending:
            return f"WAITING_{pending[0].approval_key.upper()}"
        if history_logs:
            return "COMPLETED"
        return "NOT_STARTED"
