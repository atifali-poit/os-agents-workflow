"use client";

import { useMemo, useState } from "react";
import { Background, Controls, ReactFlow, type Edge, type Node } from "@xyflow/react";
import { useQuery } from "@tanstack/react-query";

import { Card } from "@/components/ui/card";
import { api } from "@/services/api";
import type { GraphNode } from "@/types";

const employees = [
  { id: 1, name: "Sarah", role: "Finance Director" },
  { id: 2, name: "Faisal", role: "Procurement Officer" },
  { id: 3, name: "HR Manager", role: "HR Manager" }
];

const columns: Record<string, number> = {
  Invoice: 0,
  Vendor: 1,
  Workflow: 2,
  Approval: 3,
  Employee: 4,
  Department: 5,
  Agent: 2,
  Rule: 3
};

const nodeColor: Record<string, string> = {
  Invoice: "#ff7a59",
  Vendor: "#b7f7d4",
  Workflow: "#f7c948",
  Approval: "#c084fc",
  Employee: "#2ee6a6",
  Department: "#7dd3fc",
  Agent: "#c084fc",
  Rule: "#eef6f4"
};

function nodeLabel(node: GraphNode) {
  return (
    <div className="w-44">
      <div className="truncate text-sm font-semibold">{node.label}</div>
      <div className="mt-1 text-xs opacity-70">{node.type}</div>
    </div>
  );
}

export default function GraphPage() {
  const [employeeId, setEmployeeId] = useState(1);
  const graph = useQuery({
    queryKey: ["pendingApprovalGraph", employeeId],
    queryFn: () => api.pendingApprovalGraph(employeeId)
  });

  const flow = useMemo(() => {
    const rowByColumn: Record<number, number> = {};
    const nodes: Node[] = (graph.data?.nodes ?? []).map((node) => {
      const column = columns[node.type] ?? 0;
      const row = rowByColumn[column] ?? 0;
      rowByColumn[column] = row + 1;
      const color = nodeColor[node.type] ?? "#eef6f4";
      return {
        id: node.id,
        position: { x: column * 230, y: row * 118 + 40 },
        data: { label: nodeLabel(node) },
        style: {
          color,
          background: "rgba(255,255,255,0.06)",
          border: `1px solid ${color}`,
          borderRadius: 8,
          padding: 12
        }
      };
    });
    const edges: Edge[] = (graph.data?.relationships ?? []).map((relationship, index) => ({
      id: `${relationship.source}-${relationship.target}-${index}`,
      source: relationship.source,
      target: relationship.target,
      label: relationship.type,
      animated: relationship.type.includes("APPROVAL"),
      style: { stroke: "rgba(148, 163, 184, 0.7)" },
      labelStyle: { fill: "#8aa09c", fontSize: 11 }
    }));
    return { nodes, edges };
  }, [graph.data]);

  const selected = employees.find((employee) => employee.id === employeeId);
  const relationships = graph.data?.relationships ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Neo4j Approval Graph</h2>
          <p className="mt-1 text-sm text-muted">Invoice to Vendor to Workflow to Approval to Employee.</p>
        </div>
        <div className="flex gap-2">
          {employees.map((employee) => (
            <button
              key={employee.id}
              onClick={() => setEmployeeId(employee.id)}
              className={`rounded-md border px-3 py-2 text-sm transition ${
                employee.id === employeeId ? "border-accent bg-accent text-[#061013]" : "border-border bg-white/[0.06] text-muted hover:text-foreground"
              }`}
            >
              {employee.name}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_340px]">
        <Card className="h-[640px] overflow-hidden p-0">
          <ReactFlow nodes={flow.nodes} edges={flow.edges} fitView minZoom={0.35} maxZoom={1.3}>
            <Background color="rgba(148,163,184,0.22)" gap={18} />
            <Controls />
          </ReactFlow>
        </Card>

        <div className="space-y-4">
          <Card>
            <h3 className="font-semibold">{selected?.name}</h3>
            <p className="mt-1 text-sm text-muted">{selected?.role}</p>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-md bg-white/[0.06] p-3">
                <div className="text-muted">Nodes</div>
                <div className="mt-1 text-lg font-semibold">{flow.nodes.length}</div>
              </div>
              <div className="rounded-md bg-white/[0.06] p-3">
                <div className="text-muted">Edges</div>
                <div className="mt-1 text-lg font-semibold">{relationships.length}</div>
              </div>
            </div>
          </Card>
          <Card>
            <h3 className="mb-3 font-semibold">Relationships</h3>
            <div className="space-y-2">
              {relationships.map((relationship, index) => (
                <div key={`${relationship.source}-${relationship.target}-${index}`} className="rounded-md bg-white/[0.06] p-3 text-xs">
                  <div className="font-semibold text-foreground">{relationship.type}</div>
                  <div className="mt-1 text-muted">
                    {relationship.source} to {relationship.target}
                  </div>
                </div>
              ))}
              {!graph.isLoading && relationships.length === 0 ? <div className="text-sm text-muted">No pending approval graph for this employee.</div> : null}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
