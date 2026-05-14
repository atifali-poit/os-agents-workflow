"use client";

import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

import { Card } from "@/components/ui/card";

export function MetricCard({
  label,
  value,
  icon: Icon,
  tone
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone: string;
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <Card>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-muted">{label}</div>
            <div className="mt-2 text-3xl font-semibold">{value}</div>
          </div>
          <div className="flex size-11 items-center justify-center rounded-md" style={{ backgroundColor: tone }}>
            <Icon className="text-[#061013]" size={21} />
          </div>
        </div>
      </Card>
    </motion.div>
  );
}

