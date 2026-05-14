"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { api } from "@/services/api";
import type { Invoice } from "@/types";

const empty = { invoice_number: "", vendor_id: 1, amount: 0, delay_days: 0, status: "pending" };

export default function InvoicesPage() {
  const queryClient = useQueryClient();
  const invoices = useQuery({ queryKey: ["invoices"], queryFn: api.invoices });
  const vendors = useQuery({ queryKey: ["vendors"], queryFn: api.vendors });
  const [form, setForm] = useState(empty);
  const [editing, setEditing] = useState<number | null>(null);
  const refresh = () => {
    queryClient.invalidateQueries();
    setForm(empty);
    setEditing(null);
  };
  const save = useMutation({
    mutationFn: () => editing ? api.updateInvoice(editing, form) : api.createInvoice(form),
    onSuccess: refresh
  });
  const remove = useMutation({ mutationFn: api.deleteInvoice, onSuccess: refresh });
  const edit = (invoice: Invoice) => {
    setEditing(invoice.id);
    setForm({ invoice_number: invoice.invoice_number, vendor_id: invoice.vendor_id, amount: invoice.amount, delay_days: invoice.delay_days, status: invoice.status });
  };

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="mb-4 font-semibold">{editing ? "Edit Invoice" : "Create Invoice"}</h2>
        <div className="grid gap-3 md:grid-cols-6">
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" placeholder="Invoice #" value={form.invoice_number} onChange={(e) => setForm({ ...form, invoice_number: e.target.value })} />
          <select className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" value={form.vendor_id} onChange={(e) => setForm({ ...form, vendor_id: Number(e.target.value) })}>
            {(vendors.data ?? []).map((vendor) => <option key={vendor.id} value={vendor.id}>{vendor.name}</option>)}
          </select>
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" type="number" placeholder="Amount" value={form.amount} onChange={(e) => setForm({ ...form, amount: Number(e.target.value) })} />
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" type="number" placeholder="Delay" value={form.delay_days} onChange={(e) => setForm({ ...form, delay_days: Number(e.target.value) })} />
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" placeholder="Status" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} />
          <Button onClick={() => save.mutate()} disabled={save.isPending || !form.invoice_number}>Save</Button>
        </div>
      </Card>
      <EntityTable rows={invoices.data ?? []} onEdit={edit} onDelete={(id) => remove.mutate(id)} />
    </div>
  );
}

function EntityTable({ rows, onEdit, onDelete }: { rows: Invoice[]; onEdit: (invoice: Invoice) => void; onDelete: (id: number) => void }) {
  return (
    <Card>
      <h2 className="mb-4 font-semibold">Invoices</h2>
      <div className="overflow-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-muted"><tr><th className="p-2">Invoice</th><th>Vendor</th><th>Amount</th><th>Delay</th><th>Status</th><th /></tr></thead>
          <tbody>{rows.map((row) => (
            <tr key={row.id} className="border-t border-border">
              <td className="p-2">{row.invoice_number}</td><td>{row.vendor?.name}</td><td>${row.amount.toLocaleString()}</td><td>{row.delay_days}</td><td>{row.status}</td>
              <td className="flex gap-2 py-2"><Button className="bg-white/10 text-foreground" onClick={() => onEdit(row)}>Edit</Button><Button className="bg-white/10 text-foreground" onClick={() => onDelete(row.id)}>Delete</Button></td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </Card>
  );
}
