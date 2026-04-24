"use client";

import { useEffect, useState } from "react";
import { api, type AgentRow, type Decision } from "@/lib/api";

type Props = {
  agents: AgentRow[];
  lastDecisions: Decision[];
  onChanged: () => void;
};

const STRATEGIES: Record<string, string[]> = {
  "Retail Trader": ["momentum", "sentiment", "fomo"],
  "Hedge Fund":    ["directional", "risk_off", "event_driven"],
  "Quant":         ["mean_reversion", "stat_arb"],
  "Central Bank":  ["policy"],
};

export function AgentPanel({ agents, lastDecisions, onChanged }: Props) {
  const [roles, setRoles] = useState<string[]>(Object.keys(STRATEGIES));
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [role, setRole] = useState("Hedge Fund");
  const [strategy, setStrategy] = useState("directional");
  const [risk, setRisk] = useState(0.5);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.agents().then((r) => setRoles(r.roles)).catch(() => {});
  }, []);

  const decisionByAgent = new Map(lastDecisions.map((d) => [d.agent_id, d]));

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setBusy(true);
    try {
      await api.addAgent({ name: name.trim(), role, strategy, risk });
      setOpen(false);
      setName("");
      onChanged();
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    await api.removeAgent(id);
    onChanged();
  }

  return (
    <div className="panel flex flex-col h-full">
      <div className="panel-header">
        <div>
          <div className="text-sm font-semibold">Agents</div>
          <div className="text-[11px] text-arena-muted">
            {agents.length} active · last-event decisions shown
          </div>
        </div>
        <button className="btn-primary text-xs" onClick={() => setOpen((v) => !v)}>
          {open ? "Cancel" : "Add agent"}
        </button>
      </div>

      {open && (
        <form onSubmit={submit} className="px-4 py-3 border-b border-arena-border grid grid-cols-2 gap-2 text-sm">
          <input
            className="col-span-2 bg-arena-panel2 border border-arena-border rounded-md px-2 py-1.5"
            placeholder="Agent name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <select
            className="bg-arena-panel2 border border-arena-border rounded-md px-2 py-1.5"
            value={role}
            onChange={(e) => {
              setRole(e.target.value);
              setStrategy(STRATEGIES[e.target.value]?.[0] ?? "");
            }}
          >
            {roles.map((r) => <option key={r}>{r}</option>)}
          </select>
          <select
            className="bg-arena-panel2 border border-arena-border rounded-md px-2 py-1.5"
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
          >
            {(STRATEGIES[role] ?? []).map((s) => <option key={s}>{s}</option>)}
          </select>
          <label className="col-span-2 flex items-center gap-2 text-xs text-arena-muted">
            Risk {risk.toFixed(2)}
            <input
              type="range" min={0.05} max={1} step={0.05}
              value={risk} onChange={(e) => setRisk(parseFloat(e.target.value))}
              className="flex-1 accent-arena-accent"
            />
          </label>
          <button className="btn-primary col-span-2 text-xs" disabled={busy}>
            {busy ? "Adding…" : "Add"}
          </button>
        </form>
      )}

      <div className="panel-body flex-1 overflow-y-auto">
        <table className="w-full text-xs">
          <thead className="text-arena-muted">
            <tr className="text-left">
              <th className="py-1">Agent</th>
              <th>Role</th>
              <th className="text-right">Pos</th>
              <th className="text-right">PnL</th>
              <th className="text-right">Last</th>
              <th />
            </tr>
          </thead>
          <tbody className="font-mono">
            {agents.map((a) => {
              const d = decisionByAgent.get(a.id);
              const pnlTone = a.pnl > 0 ? "text-arena-bull"
                : a.pnl < 0 ? "text-arena-bear" : "text-arena-muted";
              const actTone = !d ? "text-arena-muted"
                : d.action === "buy" ? "text-arena-bull"
                : d.action === "sell" ? "text-arena-bear" : "text-arena-muted";
              return (
                <tr key={a.id} className="border-t border-arena-border/50 hover:bg-arena-panel2/60">
                  <td className="py-1.5 pr-2">
                    <div className="text-arena-text font-sans font-medium">{a.name}</div>
                    <div className="text-[10px] text-arena-muted">{a.strategy} · risk {a.risk.toFixed(2)}</div>
                  </td>
                  <td className="text-arena-muted">{a.role}</td>
                  <td className="text-right">{a.position.toFixed(1)}</td>
                  <td className={`text-right ${pnlTone}`}>
                    {a.pnl >= 0 ? "+" : ""}{a.pnl.toFixed(0)}
                  </td>
                  <td className={`text-right ${actTone}`}>
                    {d ? `${d.action.toUpperCase()} ${d.size.toFixed(0)}` : "—"}
                  </td>
                  <td className="text-right pl-2">
                    <button
                      onClick={() => remove(a.id)}
                      className="text-arena-muted hover:text-arena-bear"
                      title="Remove agent"
                    >×</button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {lastDecisions.length > 0 && (
          <div className="mt-4 pt-3 border-t border-arena-border space-y-2">
            <div className="text-[11px] uppercase tracking-wider text-arena-muted">
              Agent reasoning
            </div>
            {lastDecisions.map((d) => (
              <div key={d.agent_id} className="text-xs">
                <span className="text-arena-text font-medium">{d.agent_name}</span>
                <span className="text-arena-muted"> ({d.agent_role})</span>
                <span className={`ml-1 ${
                  d.action === "buy" ? "text-arena-bull"
                    : d.action === "sell" ? "text-arena-bear" : "text-arena-muted"
                }`}>
                  {" "}{d.action} {d.size > 0 ? d.size.toFixed(0) : ""}
                </span>
                <div className="text-[11px] text-arena-muted italic">{d.rationale}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
