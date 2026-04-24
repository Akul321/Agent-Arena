"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Run = {
  id: number;
  created_at: string;
  headline: string;
  source: string;
  sentiment: number;
  price_before: number;
  price_after: number;
  narrative: string;
  decisions: {
    agent_name: string;
    agent_role: string;
    action: string;
    size: number;
    rationale: string;
  }[];
};

export function HistoryPanel({ version }: { version: number }) {
  const [runs, setRuns] = useState<Run[] | null>(null);
  const [open, setOpen] = useState<number | null>(null);

  useEffect(() => {
    api.history().then((r) => setRuns(r.runs)).catch(() => {});
  }, [version]);

  if (!runs) return <div className="skeleton h-24" />;
  if (runs.length === 0) {
    return (
      <div className="panel-body text-sm text-arena-muted">
        No past runs yet. Inject an event to build history.
      </div>
    );
  }

  return (
    <div className="panel-body space-y-2 max-h-[320px] overflow-y-auto">
      {runs.map((r) => {
        const delta = r.price_after - r.price_before;
        const pct = (delta / r.price_before) * 100;
        const isOpen = open === r.id;
        return (
          <div
            key={r.id}
            className="rounded-lg border border-arena-border bg-arena-panel2"
          >
            <button
              onClick={() => setOpen(isOpen ? null : r.id)}
              className="w-full text-left px-3 py-2"
            >
              <div className="text-sm text-arena-text line-clamp-1">
                {r.headline}
              </div>
              <div className="flex items-center justify-between text-[11px] text-arena-muted mt-1">
                <span>{new Date(r.created_at).toLocaleTimeString()} · {r.source}</span>
                <span className={`font-mono ${
                  delta > 0 ? "text-arena-bull" : delta < 0 ? "text-arena-bear" : ""
                }`}>
                  {delta >= 0 ? "+" : ""}{pct.toFixed(2)}%
                </span>
              </div>
            </button>
            {isOpen && (
              <div className="px-3 pb-3 text-xs space-y-1 border-t border-arena-border">
                <div className="italic text-arena-muted pt-2">{r.narrative}</div>
                {r.decisions.map((d, i) => (
                  <div key={i}>
                    <span className="text-arena-text">{d.agent_name}</span>{" "}
                    <span className="text-arena-muted">({d.agent_role})</span>{" "}
                    <span className={
                      d.action === "buy" ? "text-arena-bull"
                        : d.action === "sell" ? "text-arena-bear"
                        : "text-arena-muted"
                    }>
                      {d.action} {d.size > 0 ? d.size.toFixed(0) : ""}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
