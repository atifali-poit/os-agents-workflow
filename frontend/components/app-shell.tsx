"use client";

import { Activity, Bot, FileCode2, Gauge, GitBranch, LayoutDashboard, ScrollText, ReceiptText, Truck, Users, CalendarDays, CheckSquare } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const nav = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/invoices", label: "Invoices", icon: ReceiptText },
  { href: "/vendors", label: "Vendors", icon: Truck },
  { href: "/employees", label: "Employees", icon: Users },
  { href: "/leave-requests", label: "Leave Requests", icon: CalendarDays },
  { href: "/rules", label: "Rules", icon: FileCode2 },
  { href: "/pending-approvals", label: "Pending Approvals", icon: CheckSquare },
  { href: "/runtime", label: "Runtime", icon: Gauge },
  { href: "/agents", label: "Agents", icon: Bot },
  { href: "/graph", label: "Graph", icon: GitBranch },
  { href: "/audit-logs", label: "Audit Logs", icon: ScrollText }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-border bg-[#061013]/88 p-5 backdrop-blur-xl lg:block">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex size-11 items-center justify-center rounded-lg bg-accent text-[#061013]">
            <Activity size={23} />
          </div>
          <div>
            <div className="text-lg font-bold">iGate OS</div>
            <div className="text-xs uppercase tracking-[0.22em] text-muted">Governed Runtime</div>
          </div>
        </div>
        <nav className="space-y-2">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-3 text-sm text-muted transition hover:bg-white/[0.06] hover:text-foreground",
                  active && "bg-white/10 text-foreground"
                )}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="lg:pl-72">
        <header className="sticky top-0 z-20 border-b border-border bg-[#071013]/72 px-5 py-4 backdrop-blur-xl lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-muted">Programmable enterprise operating system prototype</div>
              <h1 className="text-xl font-semibold">Deterministic AI Workflow Governance</h1>
            </div>
            <div className="hidden rounded-md border border-border px-3 py-2 text-xs text-muted md:block">
              AI translates. Runtime executes.
            </div>
          </div>
        </header>
        <div className="p-5 lg:p-8">{children}</div>
      </main>
    </div>
  );
}
