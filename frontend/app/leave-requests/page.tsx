"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { api } from "@/services/api";
import type { LeaveRequest } from "@/types";

const empty = { employee_id: 1, days: 1, status: "pending", reason: "Annual leave" };

export default function LeaveRequestsPage() {
  const queryClient = useQueryClient();
  const leaveRequests = useQuery({ queryKey: ["leaveRequests"], queryFn: api.leaveRequests });
  const employees = useQuery({ queryKey: ["employees"], queryFn: api.employees });
  const [form, setForm] = useState(empty);
  const [editing, setEditing] = useState<number | null>(null);
  const refresh = () => { queryClient.invalidateQueries(); setForm(empty); setEditing(null); };
  const save = useMutation({ mutationFn: () => editing ? api.updateLeaveRequest(editing, form) : api.createLeaveRequest(form), onSuccess: refresh });
  const remove = useMutation({ mutationFn: api.deleteLeaveRequest, onSuccess: refresh });

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="mb-4 font-semibold">{editing ? "Edit Leave Request" : "Submit Leave Request"}</h2>
        <div className="grid gap-3 md:grid-cols-5">
          <select className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: Number(e.target.value) })}>{(employees.data ?? []).map((employee) => <option key={employee.id} value={employee.id}>{employee.name}</option>)}</select>
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" type="number" value={form.days} onChange={(e) => setForm({ ...form, days: Number(e.target.value) })} />
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} />
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} />
          <Button onClick={() => save.mutate()} disabled={save.isPending}>Save</Button>
        </div>
      </Card>
      <Card>
        <h2 className="mb-4 font-semibold">Leave Requests</h2>
        <table className="w-full text-left text-sm"><thead className="text-muted"><tr><th className="p-2">Employee</th><th>Days</th><th>Reason</th><th>Status</th><th /></tr></thead><tbody>
          {(leaveRequests.data ?? []).map((leave: LeaveRequest) => <tr key={leave.id} className="border-t border-border"><td className="p-2">{leave.employee?.name}</td><td>{leave.days}</td><td>{leave.reason}</td><td>{leave.status}</td><td className="flex gap-2 py-2"><Button className="bg-white/10 text-foreground" onClick={() => { setEditing(leave.id); setForm({ employee_id: leave.employee_id, days: leave.days, status: leave.status, reason: leave.reason }); }}>Edit</Button><Button className="bg-white/10 text-foreground" onClick={() => remove.mutate(leave.id)}>Delete</Button></td></tr>)}
        </tbody></table>
      </Card>
    </div>
  );
}
