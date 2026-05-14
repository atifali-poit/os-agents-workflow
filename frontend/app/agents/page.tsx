"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bot, BriefcaseBusiness, Landmark } from "lucide-react";

import { AgentCard } from "@/components/agent-card";
import { ApprovalPanel } from "@/components/approval-panel";
import { RuntimeConsole } from "@/components/runtime-console";
import { api } from "@/services/api";
import { useRuntimeStore } from "@/store/runtime-store";

export default function AgentsPage() {
  const queryClient = useQueryClient();
  const { logs, setLogs } = useRuntimeStore();
  const approvals = useQuery({ queryKey: ["approvals"], queryFn: api.approvals });
  const mutation = useMutation({
    mutationFn: api.runAgent,
    onSuccess: (data) => {
      setLogs(data.logs);
      queryClient.invalidateQueries();
    }
  });
  const approvalMutation = useMutation({
    mutationFn: ({ approvalId, action }: { approvalId: number; action: "approved" | "rejected" }) =>
      api.decideApproval(approvalId, action),
    onSuccess: (approval) => {
      setLogs([`[ApprovalConsole] ${approval.title}: ${approval.approval_key} marked ${approval.status}`]);
      queryClient.invalidateQueries({ queryKey: ["approvals"] });
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      queryClient.invalidateQueries({ queryKey: ["auditLogs"] });
      queryClient.invalidateQueries({ queryKey: ["dashboardMetrics"] });
    }
  });
  const rows = approvals.data ?? { finance: [], procurement: [], hr: [] };

  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-3">
        <AgentCard title="Finance Agent" description="Runs active database rules against invoices and opens finance approvals." icon={Landmark} onRun={() => mutation.mutate("finance")} busy={mutation.isPending} />
        <AgentCard title="Procurement Agent" description="Runs active database rules against invoices and opens procurement approvals." icon={BriefcaseBusiness} onRun={() => mutation.mutate("procurement")} busy={mutation.isPending} />
        <AgentCard title="HR Agent" description="Runs active database rules against invoices and opens HR approvals." icon={Bot} onRun={() => mutation.mutate("hr")} busy={mutation.isPending} />
      </div>
      <div className="grid gap-4">
        <ApprovalPanel
          title="Finance Agent Dashboard"
          approvals={rows.finance}
          busy={approvalMutation.isPending}
          onDecide={(approval, action) => approvalMutation.mutate({ approvalId: approval.id, action })}
        />
        <ApprovalPanel
          title="Procurement Agent Dashboard"
          approvals={rows.procurement}
          busy={approvalMutation.isPending}
          onDecide={(approval, action) => approvalMutation.mutate({ approvalId: approval.id, action })}
        />
        <ApprovalPanel
          title="HR Agent Dashboard"
          approvals={rows.hr}
          busy={approvalMutation.isPending}
          onDecide={(approval, action) => approvalMutation.mutate({ approvalId: approval.id, action })}
        />
      </div>
      <RuntimeConsole logs={logs} />
    </div>
  );
}
