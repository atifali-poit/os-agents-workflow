from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow


@dataclass
class ApprovalDecision:
    key: str
    approved: bool


@workflow.defn
class HighValueInvoiceWorkflow:
    def __init__(self) -> None:
        self._approvals: dict[str, bool] = {}

    @workflow.run
    async def run(self, invoice_id: int, amount: float, vendor_risk_level: str) -> str:
        await workflow.execute_activity("validate_invoice_exists", invoice_id, start_to_close_timeout=timedelta(seconds=30))
        await workflow.execute_activity("check_vendor_risk_level", invoice_id, start_to_close_timeout=timedelta(seconds=30))
        if amount > 50000:
            await workflow.wait_condition(lambda: "finance_director" in self._approvals)
            if not self._approvals["finance_director"]:
                return "rejected"
        if vendor_risk_level == "high":
            await workflow.wait_condition(lambda: "procurement_officer" in self._approvals)
            if not self._approvals["procurement_officer"]:
                return "rejected"
        await workflow.execute_activity("complete_payment_processing", invoice_id, start_to_close_timeout=timedelta(seconds=30))
        return "completed"

    @workflow.signal
    async def approve(self, decision: ApprovalDecision) -> None:
        self._approvals[decision.key] = decision.approved


@workflow.defn
class VendorRiskValidationWorkflow:
    def __init__(self) -> None:
        self._approvals: dict[str, bool] = {}

    @workflow.run
    async def run(self, vendor_id: int, risk_level: str) -> str:
        await workflow.execute_activity("validate_vendor", vendor_id, start_to_close_timeout=timedelta(seconds=30))
        if risk_level == "high":
            await workflow.wait_condition(lambda: "procurement_approval" in self._approvals)
            if not self._approvals["procurement_approval"]:
                return "rejected"
        await workflow.execute_activity("complete_vendor_validation", vendor_id, start_to_close_timeout=timedelta(seconds=30))
        return "completed"

    @workflow.signal
    async def approve(self, decision: ApprovalDecision) -> None:
        self._approvals[decision.key] = decision.approved


@workflow.defn
class LeaveEscalationWorkflow:
    def __init__(self) -> None:
        self._approvals: dict[str, bool] = {}

    @workflow.run
    async def run(self, leave_request_id: int, days: int) -> str:
        await workflow.execute_activity("validate_leave_request", leave_request_id, start_to_close_timeout=timedelta(seconds=30))
        if days > 10:
            await workflow.wait_condition(lambda: "hr_manager" in self._approvals)
            if not self._approvals["hr_manager"]:
                return "rejected"
        await workflow.execute_activity("complete_leave_escalation", leave_request_id, start_to_close_timeout=timedelta(seconds=30))
        return "completed"

    @workflow.signal
    async def approve(self, decision: ApprovalDecision) -> None:
        self._approvals[decision.key] = decision.approved
