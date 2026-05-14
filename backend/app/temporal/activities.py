from temporalio import activity


@activity.defn
async def validate_invoice_exists(invoice_id: int) -> bool:
    return invoice_id > 0


@activity.defn
async def check_vendor_risk_level(invoice_id: int) -> bool:
    return invoice_id > 0


@activity.defn
async def complete_payment_processing(invoice_id: int) -> bool:
    return invoice_id > 0


@activity.defn
async def validate_vendor(vendor_id: int) -> bool:
    return vendor_id > 0


@activity.defn
async def complete_vendor_validation(vendor_id: int) -> bool:
    return vendor_id > 0


@activity.defn
async def validate_leave_request(leave_request_id: int) -> bool:
    return leave_request_id > 0


@activity.defn
async def complete_leave_escalation(leave_request_id: int) -> bool:
    return leave_request_id > 0
