import operator
import re
from dataclasses import dataclass, field

from sqlalchemy.orm import Session, joinedload

from app.models import AuditLog, Invoice, LeaveRequest, PendingApproval, Rule, Vendor
from app.services.function_registry_service import ensure_registered, parse_action


OPERATORS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
}

DOMAIN_MODELS = {
    "invoice": Invoice,
    "vendor": Vendor,
    "leave": LeaveRequest,
    "leave_request": LeaveRequest,
}


@dataclass
class RuntimeResult:
    executed_rules: int = 0
    matched_entities: int = 0
    actions_triggered: list[str] = field(default_factory=list)
    audit_logs_created: int = 0
    logs: list[str] = field(default_factory=list)


class RuntimeEngine:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, entity_type: str = "invoice", triggered_by: str = "runtime_engine") -> RuntimeResult:
        canonical = self._canonical_entity_type(entity_type)
        entities = self._entities_for(canonical)
        return self.evaluate(canonical, entities, triggered_by=triggered_by)

    def evaluate(self, entity_type: str, entities: list[object], triggered_by: str) -> RuntimeResult:
        canonical = self._canonical_entity_type(entity_type)
        rules = self._rules_for(canonical)
        result = RuntimeResult(executed_rules=len(rules))
        starting_audit_count = self.db.query(AuditLog).count()
        agent_label = self._agent_label(triggered_by)

        result.logs.append(f"[{agent_label}] Loaded {len(entities)} {canonical} records from database")
        result.logs.append(f"[{agent_label}] Loaded {len(rules)} active {canonical} rules from database")

        for rule in rules:
            for entity in entities:
                matched = self._evaluate_condition(rule.condition_expression, entity, canonical)
                result.logs.append(
                    f"[{agent_label}] Checking {self._entity_label(entity, canonical)}: "
                    f"{matched['field']} {matched['actual']} {matched['operator']} {matched['expected']} = {str(matched['result']).upper()}"
                )
                if not matched["result"]:
                    continue

                action_name, role, flags = self._parse_rule_action(rule.action_name)
                ensure_registered(self.db, action_name)
                result.matched_entities += 1
                result.actions_triggered.append(action_name)

                if action_name == "require_approval":
                    approval = self._ensure_pending_approval(rule, entity, canonical, role, flags)
                    result.logs.append(
                        f"[{agent_label}] {self._entity_label(entity, canonical)} matched {rule.name} -> "
                        f"Creating pending approval #{approval.id} for {role}"
                    )
                    self._audit(
                        canonical,
                        entity,
                        "pending_approval_created",
                        "pending",
                        f"{rule.name} created {role} approval for {self._entity_label(entity, canonical)}.",
                        triggered_by,
                        approval.workflow_id,
                    )
                else:
                    self._apply_non_approval_action(action_name, entity)
                    workflow_id = f"rule-{rule.id}-{canonical}-{getattr(entity, 'id')}-{action_name}"
                    result.logs.append(f"[{agent_label}] Executing {rule.action_name} for {self._entity_label(entity, canonical)}")
                    self._audit(
                        canonical,
                        entity,
                        action_name,
                        "success",
                        f"{rule.name} executed {rule.action_name} for {self._entity_label(entity, canonical)}.",
                        triggered_by,
                        workflow_id,
                    )

        self.db.commit()
        result.audit_logs_created = self.db.query(AuditLog).count() - starting_audit_count
        return result

    def _entities_for(self, entity_type: str) -> list[object]:
        if entity_type == "invoice":
            return self.db.query(Invoice).options(joinedload(Invoice.vendor)).order_by(Invoice.id).all()
        if entity_type == "vendor":
            return self.db.query(Vendor).order_by(Vendor.id).all()
        if entity_type == "leave":
            return self.db.query(LeaveRequest).options(joinedload(LeaveRequest.employee)).order_by(LeaveRequest.id).all()
        raise ValueError(f"Unsupported entity type: {entity_type}")

    def _rules_for(self, entity_type: str) -> list[Rule]:
        aliases = [entity_type]
        if entity_type == "leave":
            aliases.append("leave_request")
        return [
            rule
            for rule in self.db.query(Rule).filter(Rule.enabled.is_(True)).order_by(Rule.id).all()
            if rule.condition_expression.strip().split(".", 1)[0] in aliases
        ]

    def _evaluate_condition(self, expression: str, entity: object, entity_type: str) -> dict[str, object]:
        match = re.fullmatch(r"([a-z_]+)\.([a-z_]+)\s*(>=|<=|==|>|<)\s*(.+)", expression.strip())
        if not match:
            raise ValueError(f"Unsupported condition expression: {expression}")
        subject, field_name, op_symbol, raw_expected = match.groups()
        canonical_subject = self._canonical_entity_type(subject)
        if canonical_subject != entity_type:
            return {"field": field_name, "actual": "n/a", "operator": op_symbol, "expected": raw_expected, "result": False}
        actual = getattr(entity, field_name)
        expected = self._coerce(raw_expected)
        return {
            "field": field_name,
            "actual": self._display_value(actual),
            "operator": op_symbol,
            "expected": self._display_value(expected),
            "result": OPERATORS[op_symbol](actual, expected),
        }

    def _parse_rule_action(self, action_expression: str) -> tuple[str, str, str]:
        action_name, raw_argument = parse_action(action_expression)
        parts = [part.strip() for part in (raw_argument or "approval_role").split(",") if part.strip()]
        role = parts[0] if parts else "approval_role"
        flags = ",".join(parts[1:])
        return action_name, role, flags

    def _ensure_pending_approval(self, rule: Rule, entity: object, entity_type: str, role: str, flags: str) -> PendingApproval:
        workflow_id = f"rule-{rule.id}-{entity_type}-{getattr(entity, 'id')}-{role}"
        approval = (
            self.db.query(PendingApproval)
            .filter(
                PendingApproval.workflow_id == workflow_id,
                PendingApproval.entity_type == entity_type,
                PendingApproval.entity_id == getattr(entity, "id"),
                PendingApproval.required_role == role,
                PendingApproval.status == "pending",
            )
            .one_or_none()
        )
        if approval is not None:
            return approval
        approval = PendingApproval(
            workflow_id=workflow_id,
            entity_type=entity_type,
            entity_id=getattr(entity, "id"),
            required_role=role,
            flags=flags,
            status="pending",
        )
        self.db.add(approval)
        self.db.flush()
        return approval

    def _apply_non_approval_action(self, action_name: str, entity: object) -> None:
        if action_name == "escalate" and hasattr(entity, "status"):
            entity.status = "escalated"
        elif action_name == "approve_invoice" and isinstance(entity, Invoice):
            entity.status = "approved"
            entity.requires_approval = False
        elif action_name == "reject_invoice" and isinstance(entity, Invoice):
            entity.status = "rejected"
            entity.requires_approval = False

    def _audit(
        self,
        entity_type: str,
        entity: object,
        action: str,
        status: str,
        message: str,
        triggered_by: str,
        workflow_id: str | None = None,
    ) -> None:
        self.db.add(
            AuditLog(
                entity_type=entity_type,
                entity_id=getattr(entity, "id"),
                action=action,
                status=status,
                message=message,
                triggered_by=triggered_by,
                workflow_id=workflow_id,
            )
        )

    def _canonical_entity_type(self, entity_type: str) -> str:
        if entity_type == "leave_request":
            return "leave"
        if entity_type not in {"invoice", "vendor", "leave"}:
            raise ValueError(f"Unsupported entity type: {entity_type}")
        return entity_type

    def _entity_label(self, entity: object, entity_type: str) -> str:
        if entity_type == "invoice":
            return f"invoice {entity.invoice_number}"
        if entity_type == "vendor":
            return f"vendor {entity.name}"
        employee_name = entity.employee.name if getattr(entity, "employee", None) else f"employee #{entity.employee_id}"
        return f"leave request #{entity.id} for {employee_name}"

    def _agent_label(self, triggered_by: str) -> str:
        return {
            "finance_agent": "FinanceAgent",
            "procurement_agent": "ProcurementAgent",
            "hr_agent": "HRAgent",
        }.get(triggered_by, "Runtime")

    def _coerce(self, value: str) -> object:
        cleaned = value.strip().strip('"').strip("'")
        if re.fullmatch(r"\d+", cleaned):
            return int(cleaned)
        if re.fullmatch(r"\d+\.\d+", cleaned):
            return float(cleaned)
        return cleaned

    def _display_value(self, value: object) -> object:
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value
