"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Sparkles } from "lucide-react";
import { useState } from "react";

import { RuleCard } from "@/components/rule-card";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { api } from "@/services/api";

export default function RulesPage() {
  const queryClient = useQueryClient();
  const [prompt, setPrompt] = useState("If invoice exceeds 50000 require finance approval");
  const [description, setDescription] = useState("Generated from governed business intent.");
  const rules = useQuery({ queryKey: ["rules"], queryFn: api.rules });
  const translate = useMutation({ mutationFn: api.translateRule });
  const createRule = useMutation({
    mutationFn: api.createRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rules"] });
      queryClient.invalidateQueries({ queryKey: ["dashboardMetrics"] });
      queryClient.invalidateQueries({ queryKey: ["dashboardRuleActivity"] });
    }
  });
  const toggleRule = useMutation({
    mutationFn: api.toggleRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rules"] });
      queryClient.invalidateQueries({ queryKey: ["dashboardMetrics"] });
    }
  });

  const saveTranslatedRule = () => {
    if (!translate.data) return;
    createRule.mutate({
      name: `${translate.data.rule_name}_${Date.now()}`,
      description,
      condition_expression: translate.data.condition,
      action_name: translate.data.action,
      enabled: true
    });
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
      <Card>
        <div className="mb-4 flex items-center gap-2 font-semibold">
          <Sparkles size={18} className="text-accent" />
          AI Rule Translation
        </div>
        <textarea
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          className="min-h-28 w-full rounded-md border border-border bg-black/20 p-3 text-sm outline-none focus:border-accent"
        />
        <input
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          className="mt-3 h-10 w-full rounded-md border border-border bg-black/20 px-3 text-sm outline-none focus:border-accent"
        />
        <div className="mt-4 flex gap-3">
          <Button onClick={() => translate.mutate(prompt)} disabled={translate.isPending}>
            Translate
          </Button>
          <Button className="bg-gold" onClick={saveTranslatedRule} disabled={!translate.data || createRule.isPending}>
            Save Rule
          </Button>
        </div>
        {translate.data && (
          <pre className="code-panel mt-5 overflow-auto rounded-md p-4 text-xs">{translate.data.cbl}</pre>
        )}
      </Card>

      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold">Rule Registry</h2>
          <p className="text-sm text-muted">Stored CBL rules are deterministic runtime inputs.</p>
        </div>
        <div className="grid gap-4 xl:grid-cols-2">
          {(rules.data ?? []).map((rule) => (
            <div key={rule.id} className="space-y-2">
              <RuleCard rule={rule} />
              <Button className="bg-white/10 text-foreground" onClick={() => toggleRule.mutate(rule.id)}>
                {rule.enabled ? "Disable" : "Enable"}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
