import type {
  AgentApprovals,
  Approval,
  AuditLog,
  DashboardMetrics,
  DashboardRuleActivity,
  Employee,
  Invoice,
  LeaveRequest,
  PendingApprovalsGraph,
  Rule,
  RuntimeSummary,
  Translation,
  Vendor,
  WorkflowApprovalResponse,
  WorkflowStartResponse,
  WorkflowStatusResponse
} from "@/types";

const API_BASE ="http://localhost:9000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export const api = {
  invoices: () => request<Invoice[]>("/api/invoices"),
  createInvoice: (invoice: { invoice_number: string; vendor_id: number; amount: number; delay_days?: number; status?: string }) =>
    request<Invoice>("/api/invoices", { method: "POST", body: JSON.stringify(invoice) }),
  updateInvoice: (id: number, invoice: { invoice_number: string; vendor_id: number; amount: number; delay_days: number; status: string }) =>
    request<Invoice>(`/api/invoices/${id}`, { method: "PUT", body: JSON.stringify(invoice) }),
  deleteInvoice: (id: number) => request<{ deleted: boolean }>(`/api/invoices/${id}`, { method: "DELETE" }),
  vendors: () => request<Vendor[]>("/api/vendors"),
  createVendor: (vendor: { name: string; risk_level: string; country: string; status: string }) =>
    request<Vendor>("/api/vendors", { method: "POST", body: JSON.stringify(vendor) }),
  updateVendor: (id: number, vendor: { name: string; risk_level: string; country: string; status: string }) =>
    request<Vendor>(`/api/vendors/${id}`, { method: "PUT", body: JSON.stringify(vendor) }),
  deleteVendor: (id: number) => request<{ deleted: boolean }>(`/api/vendors/${id}`, { method: "DELETE" }),
  employees: () => request<Employee[]>("/api/employees"),
  createEmployee: (employee: { name: string; email: string; department: string; position: string; manager_id?: number | null }) =>
    request<Employee>("/api/employees", { method: "POST", body: JSON.stringify(employee) }),
  updateEmployee: (id: number, employee: { name: string; email: string; department: string; position: string; manager_id?: number | null }) =>
    request<Employee>(`/api/employees/${id}`, { method: "PUT", body: JSON.stringify(employee) }),
  deleteEmployee: (id: number) => request<{ deleted: boolean }>(`/api/employees/${id}`, { method: "DELETE" }),
  leaveRequests: () => request<LeaveRequest[]>("/api/leave-requests"),
  createLeaveRequest: (leave: { employee_id: number; days: number; status?: string; reason: string }) =>
    request<LeaveRequest>("/api/leave-requests", { method: "POST", body: JSON.stringify(leave) }),
  updateLeaveRequest: (id: number, leave: { employee_id: number; days: number; status: string; reason: string }) =>
    request<LeaveRequest>(`/api/leave-requests/${id}`, { method: "PUT", body: JSON.stringify(leave) }),
  deleteLeaveRequest: (id: number) => request<{ deleted: boolean }>(`/api/leave-requests/${id}`, { method: "DELETE" }),
  rules: () => request<Rule[]>("/api/rules"),
  auditLogs: () => request<AuditLog[]>("/api/audit-logs"),
  dashboardMetrics: () => request<DashboardMetrics>("/api/dashboard/metrics"),
  dashboardRuleActivity: () => request<DashboardRuleActivity[]>("/api/dashboard/rule-activity"),
  translateRule: (prompt: string) =>
    request<Translation>("/api/rules/translate", { method: "POST", body: JSON.stringify({ prompt }) }),
  createRule: (rule: {
    name: string;
    description: string;
    condition_expression: string;
    action_name: string;
    enabled: boolean;
  }) => request<Rule>("/api/rules", { method: "POST", body: JSON.stringify(rule) }),
  updateRule: (id: number, rule: {
    name: string;
    description: string;
    condition_expression: string;
    action_name: string;
    enabled: boolean;
  }) => request<Rule>(`/api/rules/${id}`, { method: "PUT", body: JSON.stringify(rule) }),
  toggleRule: (id: number) => request<Rule>(`/api/rules/${id}/toggle`, { method: "POST" }),
  executeRuntime: (entity_type = "invoice") =>
    request<RuntimeSummary>("/api/runtime/execute", { method: "POST", body: JSON.stringify({ entity_type }) }),
  runAgent: (agent: "finance" | "procurement" | "hr") =>
    request<RuntimeSummary>(`/api/agents/${agent}/run`, { method: "POST" }),
  approvals: () => request<AgentApprovals>("/api/approvals/agents"),
  allApprovals: () => request<Approval[]>("/api/approvals"),
  decideApproval: (approvalId: number, action: "approved" | "rejected") =>
    request<Approval>(`/api/approvals/${approvalId}/${action === "approved" ? "approve" : "reject"}`, { method: "POST" }),
  startInvoiceWorkflow: (invoiceId: number) =>
    request<WorkflowStartResponse>("/api/workflows/invoice/start", { method: "POST", body: JSON.stringify({ invoice_id: invoiceId }) }),
  approveWorkflow: (workflowId: string, action: "approved" | "rejected", approvalId?: number) =>
    request<WorkflowApprovalResponse>(`/api/workflows/${workflowId}/approve`, {
      method: "POST",
      body: JSON.stringify({ action, approval_id: approvalId })
    }),
  workflowStatus: (workflowId: string) => request<WorkflowStatusResponse>(`/api/workflows/${workflowId}/status`),
  pendingApprovalGraph: (employeeId: number) => request<PendingApprovalsGraph>(`/api/graph/pending/${employeeId}`)
};
