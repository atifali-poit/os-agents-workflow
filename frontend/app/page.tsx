"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, CheckSquare, FileCode2, ReceiptText, ScrollText, Truck, Users } from "lucide-react";
import { Bar, BarChart, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { MetricCard } from "@/components/metric-card";
import { Card } from "@/components/ui/card";
import { WorkflowTimeline } from "@/components/workflow-timeline";
import { api } from "@/services/api";

const colors = ["#2ee6a6", "#f7c948", "#ff7a59", "#7dd3fc"];

export default function DashboardPage() {
  const invoices = useQuery({ queryKey: ["invoices"], queryFn: api.invoices });
  const auditLogs = useQuery({ queryKey: ["auditLogs"], queryFn: api.auditLogs });
  const metrics = useQuery({ queryKey: ["dashboardMetrics"], queryFn: api.dashboardMetrics });
  const ruleActivity = useQuery({ queryKey: ["dashboardRuleActivity"], queryFn: api.dashboardRuleActivity });

  const invoiceRows = invoices.data ?? [];
  const auditRows = auditLogs.data ?? [];
  const metricRows = metrics.data;
  const statusData = Object.entries(
    invoiceRows.reduce<Record<string, number>>((acc, invoice) => {
      acc[invoice.status] = (acc[invoice.status] ?? 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));
  const activityData = ruleActivity.data ?? [];
  const auditTimeline = Object.entries(
    auditRows.reduce<Record<string, number>>((acc, log) => {
      const label = new Date(log.timestamp).toLocaleDateString(undefined, { month: "short", day: "numeric" });
      acc[label] = (acc[label] ?? 0) + 1;
      return acc;
    }, {})
  ).map(([name, logs]) => ({ name, logs }));

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total Invoices" value={metricRows?.total_invoices ?? 0} icon={ReceiptText} tone="#2ee6a6" />
        <MetricCard label="Total Vendors" value={metricRows?.total_vendors ?? 0} icon={Truck} tone="#ff7a59" />
        <MetricCard label="Total Employees" value={metricRows?.total_employees ?? 0} icon={Users} tone="#7dd3fc" />
        <MetricCard label="Pending Approvals" value={metricRows?.pending_approvals ?? 0} icon={CheckSquare} tone="#f7c948" />
        <MetricCard label="Active Rules" value={metricRows?.active_rules ?? 0} icon={FileCode2} tone="#f7c948" />
        <MetricCard label="Audit Logs" value={metricRows?.audit_logs ?? 0} icon={ScrollText} tone="#7dd3fc" />
        <MetricCard label="Agent Activity" value={metricRows?.agent_activity ?? 0} icon={Activity} tone="#b7f7d4" />
      </div>

      <WorkflowTimeline />

      <div className="grid gap-4 xl:grid-cols-3">
        <Card>
          <h2 className="mb-4 font-semibold">Invoice Status Distribution</h2>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={statusData} dataKey="value" nameKey="name" innerRadius={54} outerRadius={92}>
                {statusData.map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
        <Card>
          <h2 className="mb-4 font-semibold">Rule Execution Activity</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={activityData}>
              <XAxis dataKey="name" hide />
              <YAxis />
              <Tooltip />
              <Bar dataKey="executions" fill="#2ee6a6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card>
          <h2 className="mb-4 font-semibold">Audit Log Timeline</h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={auditTimeline}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="logs" stroke="#f7c948" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card>
        <h2 className="mb-4 font-semibold">Recent Executions</h2>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {auditRows.slice(0, 4).map((log) => (
            <div key={log.id} className="rounded-lg border border-border bg-white/[0.06] p-4">
              <div className="text-sm font-medium">{log.action}</div>
              <div className="mt-1 text-xs text-muted">{log.message}</div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
