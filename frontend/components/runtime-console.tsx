import { Terminal } from "lucide-react";

import { Card } from "@/components/ui/card";

export function RuntimeConsole({ logs }: { logs: string[] }) {
  return (
    <Card className="p-0">
      <div className="flex items-center gap-2 border-b border-border px-4 py-3 text-sm text-muted">
        <Terminal size={16} />
        Runtime Console
      </div>
      <div className="code-panel h-[360px] overflow-auto rounded-b-lg p-4 text-sm leading-7">
        {logs.length > 0 ? logs.map((log, index) => (
          <div key={`${log}-${index}`}>{log}</div>
        )) : <div className="text-muted">No runtime execution yet.</div>}
      </div>
    </Card>
  );
}
