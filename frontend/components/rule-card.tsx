import { ShieldCheck } from "lucide-react";

import { Card } from "@/components/ui/card";
import type { Rule } from "@/types";

export function RuleCard({ rule }: { rule: Rule }) {
  return (
    <Card>
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-base font-semibold">
            <ShieldCheck size={17} className="text-accent" />
            {rule.name}
          </div>
          <p className="mt-1 text-sm text-muted">{rule.description}</p>
        </div>
        <span className="rounded-md border border-border px-2 py-1 text-xs text-accent">
          {rule.enabled ? "active" : "disabled"}
        </span>
      </div>
      <pre className="code-panel overflow-auto rounded-md p-4 text-xs">
        {`RULE ${rule.name}\nIF ${rule.condition_expression}\nTHEN ${rule.action_name}`}
      </pre>
    </Card>
  );
}

