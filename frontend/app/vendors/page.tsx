"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { api } from "@/services/api";
import type { Vendor } from "@/types";

const empty = { name: "", risk_level: "low", country: "Saudi Arabia", status: "active" };

export default function VendorsPage() {
  const queryClient = useQueryClient();
  const vendors = useQuery({ queryKey: ["vendors"], queryFn: api.vendors });
  const [form, setForm] = useState(empty);
  const [editing, setEditing] = useState<number | null>(null);
  const refresh = () => { queryClient.invalidateQueries(); setForm(empty); setEditing(null); };
  const save = useMutation({ mutationFn: () => editing ? api.updateVendor(editing, form) : api.createVendor(form), onSuccess: refresh });
  const remove = useMutation({ mutationFn: api.deleteVendor, onSuccess: refresh });

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="mb-4 font-semibold">{editing ? "Edit Vendor" : "Create Vendor"}</h2>
        <div className="grid gap-3 md:grid-cols-5">
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <select className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" value={form.risk_level} onChange={(e) => setForm({ ...form, risk_level: e.target.value })}>{["low", "medium", "high", "critical"].map((risk) => <option key={risk}>{risk}</option>)}</select>
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} />
          <input className="rounded-md border border-border bg-black/20 px-3 py-2 text-sm" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} />
          <Button onClick={() => save.mutate()} disabled={save.isPending || !form.name}>Save</Button>
        </div>
      </Card>
      <Card>
        <h2 className="mb-4 font-semibold">Vendors</h2>
        <table className="w-full text-left text-sm"><thead className="text-muted"><tr><th className="p-2">Name</th><th>Risk</th><th>Country</th><th>Status</th><th /></tr></thead><tbody>
          {(vendors.data ?? []).map((vendor: Vendor) => <tr key={vendor.id} className="border-t border-border"><td className="p-2">{vendor.name}</td><td>{vendor.risk_level}</td><td>{vendor.country}</td><td>{vendor.status}</td><td className="flex gap-2 py-2"><Button className="bg-white/10 text-foreground" onClick={() => { setEditing(vendor.id); setForm({ name: vendor.name, risk_level: vendor.risk_level, country: vendor.country, status: vendor.status }); }}>Edit</Button><Button className="bg-white/10 text-foreground" onClick={() => remove.mutate(vendor.id)}>Delete</Button></td></tr>)}
        </tbody></table>
      </Card>
    </div>
  );
}
