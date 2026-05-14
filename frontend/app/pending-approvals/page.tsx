"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { api } from "@/services/api";
import { useRuntimeStore } from "@/store/runtime-store";

export default function PendingApprovalsPage() {
  const queryClient = useQueryClient();
  const { setLogs } = useRuntimeStore();
  const approvals = useQuery({ queryKey: ["allApprovals"], queryFn: api.allApprovals });
  const decide = useMutation({
    mutationFn: ({ id, action }: { id: number; action: "approved" | "rejected" }) => api.decideApproval(id, action),
    onSuccess: (approval) => {
      setLogs([`[ApprovalConsole] ${approval.title}: ${approval.approval_key} marked ${approval.status}`]);
      queryClient.invalidateQueries();
    }
  });

  return (
    <Card>
      <h2 className="mb-4 font-semibold">Pending Approvals</h2>
      <div className="overflow-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-muted"><tr><th className="p-2">Domain</th><th>Request</th><th>Role</th><th>Flags</th><th>Status</th><th>Created</th><th /></tr></thead>
          <tbody>{(approvals.data ?? []).map((approval) => (
            <tr key={approval.id} className="border-t border-border">
              <td className="p-2">{approval.entity_type}</td><td>{approval.title}<div className="text-xs text-muted">{approval.summary}</div></td><td>{approval.approval_key}</td><td>{approval.flags || "-"}</td><td>{approval.status}</td><td>{new Date(approval.pending_since).toLocaleString()}</td>
              <td className="flex gap-2 py-2">{approval.status === "pending" ? <><Button onClick={() => decide.mutate({ id: approval.id, action: "approved" })}><Check size={16} />Approve</Button><Button className="bg-white/10 text-foreground" onClick={() => decide.mutate({ id: approval.id, action: "rejected" })}><X size={16} />Reject</Button></> : null}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </Card>
  );
}
