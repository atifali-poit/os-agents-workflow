"use client";

import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { AuditTable } from "@/components/audit-table";
import { Card } from "@/components/ui/card";
import { api } from "@/services/api";

export default function AuditLogsPage() {
  const [filter, setFilter] = useState("");
  const logs = useQuery({ queryKey: ["auditLogs"], queryFn: api.auditLogs });
  const filtered = useMemo(() => {
    const query = filter.toLowerCase();
    return (logs.data ?? []).filter((log) =>
      `${log.entity_type} ${log.action} ${log.triggered_by} ${log.message}`.toLowerCase().includes(query)
    );
  }, [filter, logs.data]);

  return (
    <Card>
      <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Audit Logs</h2>
          <p className="text-sm text-muted">Every runtime and agent action is recorded.</p>
        </div>
        <input
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
          placeholder="Filter logs"
          className="h-10 rounded-md border border-border bg-black/20 px-3 text-sm outline-none focus:border-accent"
        />
      </div>
      <AuditTable logs={filtered} />
    </Card>
  );
}

