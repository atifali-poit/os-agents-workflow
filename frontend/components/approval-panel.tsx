"use client";

import { Check, GitBranch, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { WorkflowTimeline } from "@/components/workflow-timeline";
import type { Approval } from "@/types";

export function ApprovalPanel({
  title,
  approvals,
  onDecide,
  busy
}: {
  title: string;
  approvals: Approval[];
  onDecide: (approval: Approval, action: "approved" | "rejected") => void;
  busy?: boolean;
}) {
  return (
    <Card>
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="font-semibold">{title}</h2>
        <span className="rounded-md bg-white/10 px-2 py-1 text-xs text-muted">{approvals.length} pending</span>
      </div>
      <div className="space-y-4">
        {approvals.map((approval) => (
          <div key={approval.id} className="rounded-lg border border-border bg-white/[0.04] p-4">
            <div className="flex flex-col gap-3 xl:flex-row xl:items-start xl:justify-between">
              <div>
                <div className="text-sm font-semibold">{approval.title}</div>
                <div className="mt-1 text-sm text-muted">
                  {approval.summary} waiting for {approval.approver_name}
                </div>
                <div className="mt-2 flex flex-wrap gap-2 text-xs text-muted">
                  <span>Duration pending: {approval.duration_pending_days} days</span>
                  {approval.related_count > 0 ? <span>Related invoices: {approval.related_count}</span> : null}
                </div>
              </div>
              <div className="flex shrink-0 gap-2">
                <Button onClick={() => onDecide(approval, "approved")} disabled={busy}>
                  <Check size={16} />
                  Approve
                </Button>
                <Button className="bg-white/10 text-foreground" onClick={() => onDecide(approval, "rejected")} disabled={busy}>
                  <X size={16} />
                  Reject
                </Button>
                <Button className="bg-white/10 text-foreground">
                  <GitBranch size={16} />
                  View Workflow
                </Button>
              </div>
            </div>
            <div className="mt-4">
              <WorkflowTimeline steps={approval.timeline} compact />
            </div>
          </div>
        ))}
        {approvals.length === 0 ? <div className="rounded-lg border border-border bg-white/[0.04] p-4 text-sm text-muted">No pending approvals.</div> : null}
      </div>
    </Card>
  );
}
