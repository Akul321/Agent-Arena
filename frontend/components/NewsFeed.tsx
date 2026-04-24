"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type NewsItem } from "@/lib/api";

type Props = {
  onSelect: (item: NewsItem) => void;
  runningId?: string | null;
};

function timeAgo(iso: string) {
  const d = new Date(iso).getTime();
  const s = Math.max(0, Math.floor((Date.now() - d) / 1000));
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export function NewsFeed({ onSelect, runningId }: Props) {
  const [items, setItems] = useState<NewsItem[] | null>(null);
  const [sort, setSort] = useState<"recent" | "impact">("recent");
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load(force = false) {
    setRefreshing(true);
    setError(null);
    try {
      const r = await api.news(force);
      setItems(r.items);
    } catch (e: any) {
      setError(e?.message ?? "Failed to load news");
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    load();
    const iv = setInterval(() => load(false), 60_000);
    return () => clearInterval(iv);
  }, []);

  const sorted = useMemo(() => {
    if (!items) return null;
    const c = [...items];
    if (sort === "impact") c.sort((a, b) => b.impact - a.impact);
    else c.sort((a, b) =>
      new Date(b.published).getTime() - new Date(a.published).getTime());
    return c;
  }, [items, sort]);

  return (
    <div className="panel flex flex-col h-full">
      <div className="panel-header">
        <div>
          <div className="text-sm font-semibold">Live News</div>
          <div className="text-[11px] text-arena-muted">
            Free RSS · Yahoo Finance · Google News · CNBC
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-md bg-arena-panel2 border border-arena-border text-[11px]">
            <button
              className={`px-2 py-1 ${sort === "recent" ? "text-arena-accent2" : "text-arena-muted"}`}
              onClick={() => setSort("recent")}
            >Recent</button>
            <button
              className={`px-2 py-1 ${sort === "impact" ? "text-arena-accent2" : "text-arena-muted"}`}
              onClick={() => setSort("impact")}
            >Impact</button>
          </div>
          <button
            className="btn-ghost text-xs"
            onClick={() => load(true)}
            disabled={refreshing}
          >
            {refreshing ? "…" : "Refresh"}
          </button>
        </div>
      </div>

      <div className="panel-body flex-1 overflow-y-auto space-y-2">
        {error && (
          <div className="text-sm text-arena-bear">Error: {error}</div>
        )}
        {!sorted && !error && (
          <div className="space-y-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="skeleton h-16" />
            ))}
          </div>
        )}
        {sorted && sorted.length === 0 && (
          <div className="text-sm text-arena-muted">No headlines yet.</div>
        )}
        {sorted?.map((item) => {
          const tone =
            item.sentiment.label === "bullish" ? "tag-bull"
              : item.sentiment.label === "bearish" ? "tag-bear" : "tag-neutral";
          const isRunning = runningId === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelect(item)}
              disabled={isRunning}
              className="w-full text-left p-3 rounded-lg bg-arena-panel2 hover:bg-arena-border/60 border border-transparent hover:border-arena-accent/40 transition-colors disabled:opacity-60"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="text-sm text-arena-text leading-snug">
                  {item.title}
                </div>
                <span className={tone}>{item.sentiment.label}</span>
              </div>
              <div className="mt-1 flex items-center justify-between text-[11px] text-arena-muted">
                <span className="truncate max-w-[65%]">{item.source}</span>
                <span className="font-mono">
                  impact {item.impact.toFixed(2)} · {timeAgo(item.published)}
                </span>
              </div>
              {isRunning && (
                <div className="mt-2 text-[11px] text-arena-accent2">
                  Running simulation…
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
