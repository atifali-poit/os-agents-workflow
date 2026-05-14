import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from app.config import settings
from app.temporal.activities import (
    check_vendor_risk_level,
    complete_leave_escalation,
    complete_payment_processing,
    complete_vendor_validation,
    validate_invoice_exists,
    validate_leave_request,
    validate_vendor,
)
from app.temporal.workflows import HighValueInvoiceWorkflow, LeaveEscalationWorkflow, VendorRiskValidationWorkflow


async def main() -> None:
    client = await Client.connect(settings.temporal_address, namespace=settings.temporal_namespace)
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[HighValueInvoiceWorkflow, VendorRiskValidationWorkflow, LeaveEscalationWorkflow],
        activities=[
            validate_invoice_exists,
            check_vendor_risk_level,
            complete_payment_processing,
            validate_vendor,
            complete_vendor_validation,
            validate_leave_request,
            complete_leave_escalation,
        ],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
