"use client";

import type { LucideIcon } from "lucide-react";
import { Play } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function AgentCard({
  title,
  description,
  icon: Icon,
  onRun,
  busy
}: {
  title: string;
  description: string;
  icon: LucideIcon;
  onRun: () => void;
  busy?: boolean;
}) {
  return (
    <Card>
      <div className="flex items-start gap-4">
        <div className="flex size-12 items-center justify-center rounded-md bg-white/10">
          <Icon size={22} className="text-accent" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold">{title}</h3>
          <p className="mt-1 text-sm text-muted">{description}</p>
          <Button className="mt-5" onClick={onRun} disabled={busy}>
            <Play size={16} />
            {busy ? "Running" : "Run Agent"}
          </Button>
        </div>
      </div>
    </Card>
  );
}

