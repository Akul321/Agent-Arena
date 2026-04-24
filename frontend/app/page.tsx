"use client";

import { useCallback, useEffect, useState } from "react";

import { AgentPanel } from "@/components/AgentPanel";
import { EventPanel } from "@/components/EventPanel";
import { Header } from "@/components/Header";
import { HistoryPanel } from "@/components/HistoryPanel";
import { MarketChart } from "@/components/MarketChart";
import { NewsFeed } from "@/components/NewsFeed";
import {
  api,
  type AgentRow,
  type Decision,
  type MarketState,
  type NewsItem,
} from "@/lib/api";

export default function DashboardPage() {
  const [market, setMarket] = useState<MarketState | null>(null);
  const [agents, setAgents] = useState<AgentRow[]>([]);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [narrative, setNarrative] = useState<string | null>(null);
  const [shock, setShock] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [runningNewsId, setRunningNewsId] = useState<string | null>(null);
  const [resetting, setResetting] = useState(false);
  const [historyVersion, setHistoryVersion] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const refreshState = useCallback(async () => {
    try {
      const s = await api.state();
      setMarket(s.market);
      setAgents(s.agents);
    } catch (e: any) {
      setError(e?.message ?? "Backend unreachable");
    }
  }, []);

  useEffect(() => {
    refreshState();
    const iv = setInterval(refreshState, 10_000);
    return () => clearInterval(iv);
  }, [refreshState]);

  async function runEvent(payload: {
    headline: string;
    summary?: string;
    sentiment?: number;
    magnitude?: number;
    news_id?: string;
    source?: string;
  }) {
    setBusy(true);
    setError(null);
    try {
      const res = await api.runEvent(payload);
      setMarket(res.market);
      setAgents(res.agents);
      setDecisions(res.decisions);
      setNarrative(res.narrative);
      setShock(res.shock_pct);
      setHistoryVersion((v) => v + 1);
    } catch (e: any) {
      setError(e?.message ?? "Failed to run event");
    } finally {
      setBusy(false);
      setRunningNewsId(null);
    }
  }

  async function onSelectNews(item: NewsItem) {
    setRunningNewsId(item.id);
    await runEvent({
      headline: item.title,
      summary: item.summary,
      source: item.source,
      news_id: item.id,
    });
  }

  async function onReset() {
    setResetting(true);
    try {
      await api.reset();
      setDecisions([]);
      setNarrative(null);
      setShock(null);
      await refreshState();
      setHistoryVersion((v) => v + 1);
    } finally {
      setResetting(false);
    }
  }

  return (
    <div className="min-h-screen">
      <Header market={market} onReset={onReset} resetting={resetting} />
      {error && (
        <div className="max-w-[1600px] mx-auto px-6 mt-4">
          <div className="panel panel-body text-sm text-arena-bear">
            {error}
          </div>
        </div>
      )}

      <main className="max-w-[1600px] mx-auto px-6 py-6 grid grid-cols-12 gap-4">
        {/* Left: News */}
        <section className="col-span-12 xl:col-span-3 min-h-[520px]">
          <NewsFeed onSelect={onSelectNews} runningId={runningNewsId} />
        </section>

        {/* Center: Chart + Event */}
        <section className="col-span-12 xl:col-span-6 space-y-4">
          <div className="panel">
            <div className="panel-header">
              <div>
                <div className="text-sm font-semibold">
                  Market · {market?.ticker ?? "—"}
                </div>
                <div className="text-[11px] text-arena-muted">
                  Simulated price tape. Dashed lines mark event ticks.
                </div>
              </div>
            </div>
            <MarketChart tape={market?.tape ?? []} shock={shock} />
          </div>
          <EventPanel onSubmit={runEvent} busy={busy} lastNarrative={narrative} />
        </section>

        {/* Right: Agents */}
        <section className="col-span-12 xl:col-span-3 min-h-[520px]">
          <AgentPanel
            agents={agents}
            lastDecisions={decisions}
            onChanged={refreshState}
          />
        </section>

        {/* Bottom: History */}
        <section className="col-span-12">
          <div className="panel">
            <div className="panel-header">
              <div>
                <div className="text-sm font-semibold">Replay</div>
                <div className="text-[11px] text-arena-muted">
                  Past simulations — click to expand agent decisions.
                </div>
              </div>
            </div>
            <HistoryPanel version={historyVersion} />
          </div>
        </section>
      </main>
    </div>
  );
}
