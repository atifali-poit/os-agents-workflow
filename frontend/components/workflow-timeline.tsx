import { Check, Clock3 } from "lucide-react";

import type { WorkflowTimelineStep } from "@/types";

const defaultSteps: WorkflowTimelineStep[] = [
  { label: "Human Intent", state: "complete", complete: true },
  { label: "AI Translation", state: "complete", complete: true },
  { label: "Computable Rule", state: "complete", complete: true },
  { label: "Temporal Workflow", state: "current", complete: false },
  { label: "Approval Signal", state: "pending", complete: false },
  { label: "Audit Logs", state: "pending", complete: false }
];

export function WorkflowTimeline({ steps = defaultSteps, compact = false }: { steps?: WorkflowTimelineStep[]; compact?: boolean }) {
  return (
    <div className={`grid gap-3 ${compact ? "md:grid-cols-3" : "md:grid-cols-6"}`}>
      {steps.map((step, index) => (
        <div key={`${step.label}-${index}`} className="rounded-lg border border-border bg-white/[0.06] p-4">
          <div
            className={`mb-3 flex size-8 items-center justify-center rounded-md text-sm font-bold ${
              step.complete ? "bg-accent text-[#061013]" : step.state === "current" ? "bg-[#f7c948] text-[#171109]" : "bg-white/10 text-muted"
            }`}
          >
            {step.complete ? <Check size={16} /> : step.state === "current" ? <Clock3 size={16} /> : index + 1}
          </div>
          <div className="text-sm font-medium">{step.label}</div>
          <div className="mt-1 text-xs capitalize text-muted">{step.state}</div>
        </div>
      ))}
    </div>
  );
}
