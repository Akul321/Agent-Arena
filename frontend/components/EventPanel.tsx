"use client";

import { useState } from "react";

type Props = {
  onSubmit: (v: {
    headline: string;
    summary?: string;
    sentiment?: number;
    magnitude?: number;
  }) => void;
  busy?: boolean;
  lastNarrative?: string | null;
};

const PRESETS = [
  { label: "Fed hikes 50bps", headline: "Fed hikes rates 50bps, signals more to come", sentiment: -0.6, magnitude: 0.9 },
  { label: "Rate cut",        headline: "Federal Reserve cuts rates, cites slowing growth",  sentiment: +0.5, magnitude: 0.85 },
  { label: "Beat earnings",   headline: "Tech giant crushes earnings, guidance raised",      sentiment: +0.7, magnitude: 0.8 },
  { label: "Miss earnings",   headline: "Retailer misses earnings, slashes outlook",         sentiment: -0.7, magnitude: 0.8 },
  { label: "Geopolitical",    headline: "Sanctions expand as geopolitical tensions flare",   sentiment: -0.5, magnitude: 0.8 },
];

export function EventPanel({ onSubmit, busy, lastNarrative }: Props) {
  const [headline, setHeadline] = useState("");
  const [summary, setSummary] = useState("");
  const [sentiment, setSentiment] = useState<number | null>(null);
  const [magnitude, setMagnitude] = useState<number | null>(null);

  function send() {
    if (!headline.trim()) return;
    onSubmit({
      headline: headline.trim(),
      summary: summary.trim() || undefined,
      sentiment: sentiment ?? undefined,
      magnitude: magnitude ?? undefined,
    });
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <div className="text-sm font-semibold">Inject event</div>
          <div className="text-[11px] text-arena-muted">
            Write a headline or pick a preset; leave score blank to auto-score.
          </div>
        </div>
      </div>
      <div className="panel-body space-y-3">
        <input
          className="w-full bg-arena-panel2 border border-arena-border rounded-md px-3 py-2 text-sm"
          placeholder="e.g. AAPL beats earnings, guides higher"
          value={headline}
          onChange={(e) => setHeadline(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <textarea
          className="w-full bg-arena-panel2 border border-arena-border rounded-md px-3 py-2 text-sm h-16 resize-none"
          placeholder="Optional detail…"
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
        />
        <div className="grid grid-cols-2 gap-3 text-xs">
          <label className="flex flex-col gap-1">
            <span className="text-arena-muted">
              Sentiment {sentiment === null ? "(auto)" : sentiment.toFixed(2)}
            </span>
            <input
              type="range" min={-1} max={1} step={0.05}
              value={sentiment ?? 0}
              onChange={(e) => setSentiment(parseFloat(e.target.value))}
              className="accent-arena-accent"
            />
            <button
              className="text-[10px] text-arena-muted hover:text-arena-accent2 self-start"
              type="button"
              onClick={() => setSentiment(null)}
            >reset to auto</button>
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-arena-muted">
              Magnitude {magnitude === null ? "(auto)" : magnitude.toFixed(2)}
            </span>
            <input
              type="range" min={0} max={1} step={0.05}
              value={magnitude ?? 0.6}
              onChange={(e) => setMagnitude(parseFloat(e.target.value))}
              className="accent-arena-accent"
            />
            <button
              className="text-[10px] text-arena-muted hover:text-arena-accent2 self-start"
              type="button"
              onClick={() => setMagnitude(null)}
            >reset to auto</button>
          </label>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {PRESETS.map((p) => (
            <button
              key={p.label}
              type="button"
              className="text-[11px] px-2 py-1 rounded-md bg-arena-panel2 border border-arena-border hover:border-arena-accent/60"
              onClick={() => {
                setHeadline(p.headline);
                setSentiment(p.sentiment);
                setMagnitude(p.magnitude);
              }}
            >
              {p.label}
            </button>
          ))}
        </div>

        <button className="btn-primary w-full" disabled={busy || !headline.trim()} onClick={send}>
          {busy ? "Running…" : "Run simulation step"}
        </button>

        {lastNarrative && (
          <div className="text-xs text-arena-muted border-t border-arena-border pt-3 italic">
            {lastNarrative}
          </div>
        )}
      </div>
    </div>
  );
}
