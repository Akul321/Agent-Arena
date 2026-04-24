"use client";

import type { MarketState } from "@/lib/api";

type Props = {
  market: MarketState | null;
  onReset: () => void;
  resetting?: boolean;
};

function fmt(n: number | undefined, digits = 2) {
  if (n === undefined || !Number.isFinite(n)) return "—";
  return n.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function Header({ market, onReset, resetting }: Props) {
  const price = market?.price;
  const sentiment = market?.sentiment ?? 0;
  const trend = market?.trend ?? 0;
  const vol = market?.volatility ?? 0;

  const stats = [
    { label: "Price", value: fmt(price, 2), tone: "text-arena-text" },
    {
      label: "Sentiment",
      value: `${sentiment >= 0 ? "+" : ""}${fmt(sentiment, 2)}`,
      tone: sentiment > 0.05 ? "text-arena-bull"
          : sentiment < -0.05 ? "text-arena-bear"
          : "text-arena-muted",
    },
    {
      label: "Trend",
      value: `${trend >= 0 ? "+" : ""}${fmt(trend, 2)}`,
      tone: trend > 0 ? "text-arena-bull" : trend < 0 ? "text-arena-bear" : "text-arena-muted",
    },
    {
      label: "Vol",
      value: fmt(vol * 100, 2) + "%",
      tone: "text-arena-text",
    },
  ];

  return (
    <header className="border-b border-arena-border bg-arena-bg/80 backdrop-blur sticky top-0 z-20">
      <div className="max-w-[1600px] mx-auto px-6 py-3 flex items-center gap-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-md bg-gradient-to-br from-arena-accent to-arena-accent2 shadow-glow" />
          <div>
            <div className="text-lg font-semibold tracking-tight">
              Agent Arena
            </div>
            <div className="text-[11px] text-arena-muted -mt-0.5">
              Multi-agent market simulation · {market?.ticker ?? "—"}
            </div>
          </div>
        </div>

        <div className="flex-1" />

        <div className="flex items-center gap-6">
          {stats.map((s) => (
            <div key={s.label} className="text-right">
              <div className="text-[10px] uppercase tracking-wider text-arena-muted">
                {s.label}
              </div>
              <div className={`font-mono text-sm ${s.tone}`}>{s.value}</div>
            </div>
          ))}
          <button
            onClick={onReset}
            disabled={resetting}
            className="btn-ghost"
            title="Reset market and agents"
          >
            {resetting ? "Resetting…" : "Reset"}
          </button>
        </div>
      </div>
    </header>
  );
}
