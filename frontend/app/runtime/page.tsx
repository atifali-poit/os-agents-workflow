"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { PlayCircle } from "lucide-react";

import { RuntimeConsole } from "@/components/runtime-console";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { api } from "@/services/api";
import { useRuntimeStore } from "@/store/runtime-store";

export default function RuntimePage() {
  const queryClient = useQueryClient();
  const { logs, setLogs } = useRuntimeStore();
  const runtime = useMutation({
    mutationFn: () => api.executeRuntime("invoice"),
    onSuccess: (data) => {
      setLogs(data.logs);
      queryClient.invalidateQueries();
    }
  });

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
      <RuntimeConsole logs={logs} />
      <div className="space-y-4">
        <Card>
          <h2 className="font-semibold">Runtime Engine</h2>
          <p className="mt-2 text-sm text-muted">
            Runtime evaluates enabled database rules against database invoices, records pending approval waits, and writes audit logs.
          </p>
          <Button className="mt-5 w-full" onClick={() => runtime.mutate()} disabled={runtime.isPending}>
            <PlayCircle size={17} />
            Execute Invoice Workflow
          </Button>
        </Card>
        {runtime.data && (
          <Card>
            <h3 className="mb-3 font-semibold">Execution Summary</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-muted">Executed Rules</span><span>{runtime.data.executed_rules}</span></div>
              <div className="flex justify-between"><span className="text-muted">Matched Entities</span><span>{runtime.data.matched_entities}</span></div>
              <div className="flex justify-between"><span className="text-muted">Audit Logs</span><span>{runtime.data.audit_logs_created}</span></div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
