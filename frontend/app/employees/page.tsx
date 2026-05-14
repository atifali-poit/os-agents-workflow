"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { api } from "@/services/api";
import type { Employee } from "@/types";

const empty = { name: "", email: "", department: "Finance", position: "", manager_id: null as number | null };

export default function EmployeesPage() {
  const queryClient = useQueryClient();
  const employees = useQuery({ queryKey: ["employees"], queryFn: api.employees });
  const [form, setForm] = useState(empty);
  const [editing, setEditing] = useState<number | null>(null);
  const refresh = () => { queryClient.invalidateQueries(); setForm(empty); setEditing(null); };
  const save = useMutation({ mutationFn: () => editing ? api.updateEmployee(editing, form) : api.createEmployee(form), onSuccess: refresh });
  const remove = useMutation({ mutationFn: api.deleteEmployee, onSuccess: refresh });

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="mb-4 font-semibold">{editing ? "Edit Employee" : "Create Employee"}</h2>
        <div className="grid gap-3 md:grid-cols-6">
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" placeholder="Department" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" placeholder="Position" value={form.position} onChange={(e) => setForm({ ...form, position: e.target.value })} />
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" type="number" placeholder="Manager ID" value={form.manager_id ?? ""} onChange={(e) => setForm({ ...form, manager_id: e.target.value ? Number(e.target.value) : null })} />
          <Button onClick={() => save.mutate()} disabled={save.isPending || !form.name || !form.email}>Save</Button>
        </div>
      </Card>
      <Card>
        <h2 className="mb-4 font-semibold">Employees</h2>
        <table className="w-full text-left text-sm"><thead className="text-muted"><tr><th className="p-2">Name</th><th>Email</th><th>Department</th><th>Position</th><th>Manager</th><th /></tr></thead><tbody>
          {(employees.data ?? []).map((employee: Employee) => <tr key={employee.id} className="border-t border-border"><td className="p-2">{employee.name}</td><td>{employee.email}</td><td>{employee.department?.name}</td><td>{employee.position}</td><td>{employee.manager_id ?? "-"}</td><td className="flex gap-2 py-2"><Button className="bg-white/10 text-foreground" onClick={() => { setEditing(employee.id); setForm({ name: employee.name, email: employee.email, department: employee.department?.name ?? "", position: employee.position, manager_id: employee.manager_id ?? null }); }}>Edit</Button><Button className="bg-white/10 text-foreground" onClick={() => remove.mutate(employee.id)}>Delete</Button></td></tr>)}
        </tbody></table>
      </Card>
    </div>
  );
}
