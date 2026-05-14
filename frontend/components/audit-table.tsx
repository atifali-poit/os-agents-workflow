import type { AuditLog } from "@/types";

export function AuditTable({ logs }: { logs: AuditLog[] }) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full min-w-[760px] border-collapse text-sm">
        <thead className="bg-white/[0.07] text-left text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Timestamp</th>
            <th className="px-4 py-3 font-medium">Entity</th>
            <th className="px-4 py-3 font-medium">Action</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3 font-medium">Triggered By</th>
            <th className="px-4 py-3 font-medium">Message</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id} className="border-t border-border">
              <td className="px-4 py-3 text-muted">{new Date(log.timestamp).toLocaleString()}</td>
              <td className="px-4 py-3">{log.entity_type} #{log.entity_id}</td>
              <td className="px-4 py-3">{log.action}</td>
              <td className="px-4 py-3 text-accent">{log.status}</td>
              <td className="px-4 py-3">{log.triggered_by}</td>
              <td className="px-4 py-3 text-muted">{log.message}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
