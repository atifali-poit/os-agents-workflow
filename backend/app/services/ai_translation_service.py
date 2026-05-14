import re

from app.schemas import TranslateResponse


def translate_prompt(prompt: str) -> TranslateResponse:
    normalized = prompt.strip().lower()

    invoice_match = re.search(r"invoice (?:exceeds|above|over|greater than) (\d+)", normalized)
    if invoice_match and "finance" in normalized:
        amount = invoice_match.group(1)
        return _response(
            "high_value_invoice",
            f"invoice.amount > {amount}",
            "require_approval(finance_director)",
        )

    payment_match = re.search(r"payment delayed more than (\d+) days", normalized)
    if payment_match:
        days = payment_match.group(1)
        action = "notify(finance_team)" if "notify" in normalized else "escalate(finance_team)"
        return _response("overdue_payment", f"invoice.delay_days > {days}", action)

    if "vendor" in normalized and "high risk" in normalized and "procurement" in normalized:
        return _response(
            "risky_vendor",
            'vendor.risk_level == "high"',
            "require_approval(procurement_officer)",
        )

    leave_match = re.search(r"leave exceeds (\d+) days", normalized)
    if leave_match and ("hr" in normalized or "human resources" in normalized):
        days = leave_match.group(1)
        return _response("leave_escalation", f"leave_request.days > {days}", "require_approval(hr_manager)")

    raise ValueError("Prompt pattern is not supported by the deterministic translator.")


def _response(rule_name: str, condition: str, action: str) -> TranslateResponse:
    return TranslateResponse(
        rule_name=rule_name,
        condition=condition,
        action=action,
        cbl=f"RULE {rule_name}: IF {condition} THEN {action}",
    )

