import asyncio
from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models import ApprovalRequest, AuditLog, Employee, Invoice, LeaveRequest, Vendor
from app.runtime.runtime_engine import RuntimeResult
from app.services.approval_service import ensure_seed_approval


class TemporalOrchestrationService:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, entity_type: str, triggered_by: str) -> RuntimeResult:
        result = RuntimeResult()
        starting_audit_count = self.db.query(AuditLog).count()

        if entity_type == "invoice":
            self._run_high_value_invoice_workflows(result, triggered_by)
        elif entity_type == "vendor":
            self._run_vendor_risk_workflows(result, triggered_by)
        elif entity_type == "leave_request":
            self._run_leave_workflows(result, triggered_by)
        else:
            raise ValueError(f"Unsupported entity type: {entity_type}")

        self.db.commit()
        result.audit_logs_created = self.db.query(AuditLog).count() - starting_audit_count
        return result

    def _run_high_value_invoice_workflows(self, result: RuntimeResult, triggered_by: str) -> None:
        invoices = self.db.query(Invoice).options(joinedload(Invoice.vendor)).filter(Invoice.status == "pending").all()
        result.executed_rules = 2
        for invoice in invoices:
            approval_keys: list[tuple[str, int]] = []
            if invoice.amount > 50000:
                employee = self._employee_by_position("Finance Director")
                approval_keys.append(("finance_director", employee.id))
            if invoice.vendor and invoice.vendor.risk_level == "high":
                employee = self._employee_by_position("Procurement Officer")
                approval_keys.append(("procurement_officer", employee.id))
            if not approval_keys:
                continue

            invoice.requires_approval = True
            invoice.status = "escalated"
            result.matched_entities += 1
            result.actions_triggered.append("HighValueInvoiceWorkflow")
            result.logs.append(f"[Temporal] HighValueInvoiceWorkflow started for {invoice.invoice_number}")
            workflow_id = f"high-value-invoice-{invoice.id}"
            self._maybe_start_temporal_workflow(
                "HighValueInvoiceWorkflow",
                workflow_id,
                invoice.id,
                invoice.amount,
                invoice.vendor.risk_level if invoice.vendor else "low",
                result.logs,
            )
            for approval_key, approver_id in approval_keys:
                ensure_seed_approval(
                    self.db,
                    workflow_name="HighValueInvoiceWorkflow",
                    workflow_id=workflow_id,
                    workflow_run_id=f"high-value-invoice-{invoice.id}-{approval_key}",
                    entity_type="invoice",
                    entity_id=invoice.id,
                    approval_key=approval_key,
                    approver_employee_id=approver_id,
                    details=f"{invoice.invoice_number} waiting for {approval_key}",
                    days_pending=2 if invoice.invoice_number == "INV-001" and approval_key == "finance_director" else 0,
                )
                result.logs.append(f"[Temporal] Waiting for {approval_key} approval")
            self._audit("invoice", invoice.id, "workflow_waiting_for_approval", triggered_by, workflow_id)

    def _run_vendor_risk_workflows(self, result: RuntimeResult, triggered_by: str) -> None:
        vendors = self.db.query(Vendor).filter(Vendor.risk_level == "high").all()
        result.executed_rules = 1
        approver = self._employee_by_position("Procurement Officer")
        for vendor in vendors:
            result.matched_entities += 1
            result.actions_triggered.append("VendorRiskValidationWorkflow")
            result.logs.append(f"[Temporal] VendorRiskValidationWorkflow started for {vendor.name}")
            workflow_id = f"vendor-risk-{vendor.id}"
            self._maybe_start_temporal_workflow(
                "VendorRiskValidationWorkflow",
                workflow_id,
                vendor.id,
                vendor.risk_level,
                result.logs,
            )
            ensure_seed_approval(
                self.db,
                workflow_name="VendorRiskValidationWorkflow",
                workflow_id=workflow_id,
                workflow_run_id=f"vendor-risk-{vendor.id}-procurement_approval",
                entity_type="vendor",
                entity_id=vendor.id,
                approval_key="procurement_approval",
                approver_employee_id=approver.id,
                details=f"{vendor.name} high-risk validation",
            )
            result.logs.append("[Temporal] Waiting for procurement_approval")
            self._audit("vendor", vendor.id, "workflow_waiting_for_approval", triggered_by, workflow_id)

    def _run_leave_workflows(self, result: RuntimeResult, triggered_by: str) -> None:
        leave_requests = self.db.query(LeaveRequest).filter(LeaveRequest.status == "pending", LeaveRequest.days > 10).all()
        result.executed_rules = 1
        approver = self._employee_by_position("HR Manager")
        for leave_request in leave_requests:
            result.matched_entities += 1
            result.actions_triggered.append("LeaveEscalationWorkflow")
            result.logs.append(f"[Temporal] LeaveEscalationWorkflow started for employee #{leave_request.employee_id}")
            workflow_id = f"leave-escalation-{leave_request.id}"
            self._maybe_start_temporal_workflow(
                "LeaveEscalationWorkflow",
                workflow_id,
                leave_request.id,
                leave_request.days,
                result.logs,
            )
            ensure_seed_approval(
                self.db,
                workflow_name="LeaveEscalationWorkflow",
                workflow_id=workflow_id,
                workflow_run_id=f"leave-escalation-{leave_request.id}-hr_manager",
                entity_type="leave_request",
                entity_id=leave_request.id,
                approval_key="hr_manager",
                approver_employee_id=approver.id,
                details=f"Employee #{leave_request.employee_id} requested {leave_request.days} days",
            )
            result.logs.append("[Temporal] Waiting for hr_manager approval")
            self._audit("leave_request", leave_request.id, "workflow_waiting_for_approval", triggered_by, workflow_id)

    def _employee_by_position(self, position: str) -> Employee:
        employee = self.db.query(Employee).filter(Employee.position == position).one()
        return employee

    def _audit(self, entity_type: str, entity_id: int, action: str, triggered_by: str, workflow_id: str) -> None:
        self.db.add(
            AuditLog(
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                status="pending",
                message=f"Temporal workflow is waiting on an approval signal; workflow_id={workflow_id}.",
                triggered_by=triggered_by,
                workflow_id=workflow_id,
                timestamp=datetime.utcnow(),
            )
        )

    def _maybe_start_temporal_workflow(self, workflow_name: str, workflow_id: str, *args: object) -> None:
        logs = args[-1]
        workflow_args = args[:-1]
        if not settings.temporal_enabled:
            logs.append("[Temporal] Local approval state recorded; set TEMPORAL_ENABLED=true to dispatch to Temporal.")
            return

        async def start() -> None:
            from temporalio.client import Client

            client = await Client.connect(settings.temporal_address, namespace=settings.temporal_namespace)
            await client.start_workflow(
                workflow_name,
                *workflow_args,
                id=workflow_id,
                task_queue=settings.temporal_task_queue,
            )

        try:
            asyncio.run(start())
        except Exception as exc:
            logs.append(f"[Temporal] Dispatch failed, approval state kept locally: {exc}")
