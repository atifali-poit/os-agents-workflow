from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class VendorOut(ORMModel):
    id: int
    name: str
    country: str
    risk_level: str
    status: str
    created_at: datetime


class VendorCreate(BaseModel):
    name: str
    risk_level: str
    country: str
    status: str = "active"


class VendorUpdate(BaseModel):
    name: str
    risk_level: str
    country: str
    status: str


class InvoiceCreate(BaseModel):
    invoice_number: str
    vendor_id: int
    amount: float
    status: str = "pending"
    delay_days: int = 0
    requires_approval: bool = False


class InvoiceOut(ORMModel):
    id: int
    invoice_number: str
    vendor_id: int
    amount: float
    status: str
    delay_days: int
    requires_approval: bool
    created_at: datetime
    vendor: VendorOut | None = None


class InvoiceUpdate(BaseModel):
    invoice_number: str
    vendor_id: int
    amount: float
    status: str
    delay_days: int = 0


class RuleCreate(BaseModel):
    name: str
    description: str
    condition_expression: str
    action_name: str
    enabled: bool = True
    created_by: str = "user"


class RuleOut(ORMModel):
    id: int
    name: str
    description: str
    condition_expression: str
    action_name: str
    enabled: bool
    created_by: str
    created_at: datetime


class RuleUpdate(BaseModel):
    name: str
    description: str
    condition_expression: str
    action_name: str
    enabled: bool


class DepartmentOut(ORMModel):
    id: int
    name: str


class EmployeeCreate(BaseModel):
    name: str
    email: str
    department: str
    position: str
    manager_id: int | None = None


class EmployeeUpdate(EmployeeCreate):
    pass


class EmployeeOut(ORMModel):
    id: int
    name: str
    email: str
    department_id: int
    position: str
    manager_id: int | None = None
    created_at: datetime
    department: DepartmentOut | None = None


class LeaveRequestCreate(BaseModel):
    employee_id: int
    days: int
    status: str = "pending"
    reason: str


class LeaveRequestUpdate(LeaveRequestCreate):
    pass


class LeaveRequestOut(ORMModel):
    id: int
    employee_id: int
    days: int
    status: str
    reason: str
    created_at: datetime
    employee: EmployeeOut | None = None


class TranslateRequest(BaseModel):
    prompt: str


class TranslateResponse(BaseModel):
    rule_name: str
    condition: str
    action: str
    cbl: str


class RuntimeRequest(BaseModel):
    entity_type: str = "invoice"


class RuntimeSummary(BaseModel):
    executed_rules: int
    matched_entities: int
    actions_triggered: list[str]
    audit_logs_created: int
    logs: list[str]


class DashboardMetrics(BaseModel):
    total_invoices: int
    total_vendors: int
    total_employees: int
    pending_approvals: int
    escalated_invoices: int
    active_rules: int
    audit_logs: int
    agent_activity: int


class DashboardRuleActivity(BaseModel):
    name: str
    executions: int


class AuditLogOut(ORMModel):
    id: int
    entity_type: str
    entity_id: int
    action: str
    status: str
    message: str
    triggered_by: str
    workflow_id: str | None = None
    timestamp: datetime


class ApprovalActionRequest(BaseModel):
    action: str
    approval_id: int | None = None


class ApprovalOut(ORMModel):
    id: int
    workflow_name: str
    workflow_id: str
    workflow_run_id: str | None = None
    entity_type: str
    entity_id: int
    approval_key: str
    flags: str = ""
    approver_employee_id: int | None = None
    approver_name: str
    approver_role: str
    department: str
    status: str
    pending_since: datetime
    duration_pending_days: int
    title: str
    summary: str
    related_count: int = 0
    timeline: list[dict[str, str | bool]]


class AgentApprovalsOut(BaseModel):
    finance: list[ApprovalOut]
    procurement: list[ApprovalOut]
    hr: list[ApprovalOut]


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphRelationship(BaseModel):
    source: str
    target: str
    type: str


class PendingApprovalsGraph(BaseModel):
    employee_id: int
    nodes: list[GraphNode]
    relationships: list[GraphRelationship]


class InvoiceWorkflowStartRequest(BaseModel):
    invoice_id: int


class WorkflowStartResponse(BaseModel):
    workflow_id: str
    run_id: str
    status: str
    pending_approvals: list[ApprovalOut]


class WorkflowApprovalResponse(BaseModel):
    workflow_id: str
    status: str
    resumed: bool
    pending_approvals: list[ApprovalOut]


class WorkflowStatusResponse(BaseModel):
    workflow_id: str
    workflow_name: str
    status: str
    current_step: str
    pending_approvals: list[ApprovalOut]
    history: list[dict[str, str]]
