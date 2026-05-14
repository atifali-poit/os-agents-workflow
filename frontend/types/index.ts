export type Vendor = {
  id: number;
  name: string;
  country: string;
  risk_level: string;
  status: string;
  created_at: string;
};

export type Invoice = {
  id: number;
  invoice_number: string;
  vendor_id: number;
  amount: number;
  status: string;
  delay_days: number;
  requires_approval: boolean;
  created_at: string;
  vendor?: Vendor;
};

export type Rule = {
  id: number;
  name: string;
  description: string;
  condition_expression: string;
  action_name: string;
  enabled: boolean;
  created_by: string;
  created_at: string;
};

export type AuditLog = {
  id: number;
  entity_type: string;
  entity_id: number;
  action: string;
  status: string;
  message: string;
  triggered_by: string;
  workflow_id?: string | null;
  timestamp: string;
};

export type RuntimeSummary = {
  executed_rules: number;
  matched_entities: number;
  actions_triggered: string[];
  audit_logs_created: number;
  logs: string[];
};

export type DashboardMetrics = {
  total_invoices: number;
  total_vendors: number;
  total_employees: number;
  pending_approvals: number;
  escalated_invoices: number;
  active_rules: number;
  audit_logs: number;
  agent_activity: number;
};

export type DashboardRuleActivity = {
  name: string;
  executions: number;
};

export type Translation = {
  rule_name: string;
  condition: string;
  action: string;
  cbl: string;
};

export type WorkflowTimelineStep = {
  label: string;
  state: string;
  complete: boolean;
};

export type Approval = {
  id: number;
  workflow_name: string;
  workflow_id: string;
  workflow_run_id: string;
  entity_type: string;
  entity_id: number;
  approval_key: string;
  flags: string;
  approver_employee_id?: number | null;
  approver_name: string;
  approver_role: string;
  department: string;
  status: string;
  pending_since: string;
  duration_pending_days: number;
  title: string;
  summary: string;
  related_count: number;
  timeline: WorkflowTimelineStep[];
};

export type Department = {
  id: number;
  name: string;
};

export type Employee = {
  id: number;
  name: string;
  email: string;
  department_id: number;
  position: string;
  manager_id?: number | null;
  created_at: string;
  department?: Department | null;
};

export type LeaveRequest = {
  id: number;
  employee_id: number;
  days: number;
  status: string;
  reason: string;
  created_at: string;
  employee?: Employee | null;
};

export type AgentApprovals = {
  finance: Approval[];
  procurement: Approval[];
  hr: Approval[];
};

export type GraphNode = {
  id: string;
  label: string;
  type: string;
};

export type GraphRelationship = {
  source: string;
  target: string;
  type: string;
};

export type PendingApprovalsGraph = {
  employee_id: number;
  nodes: GraphNode[];
  relationships: GraphRelationship[];
};

export type WorkflowStartResponse = {
  workflow_id: string;
  run_id: string;
  status: string;
  pending_approvals: Approval[];
};

export type WorkflowApprovalResponse = {
  workflow_id: string;
  status: string;
  resumed: boolean;
  pending_approvals: Approval[];
};

export type WorkflowStatusResponse = {
  workflow_id: string;
  workflow_name: string;
  status: string;
  current_step: string;
  pending_approvals: Approval[];
  history: { timestamp: string; action: string; status: string; message: string }[];
};
