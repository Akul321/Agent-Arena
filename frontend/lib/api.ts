// In the single-container deploy the backend also serves the UI, so API
// calls are relative. In dev (`next dev`) the backend lives on port 8000,
// so default to that. Override explicitly with NEXT_PUBLIC_API_URL for
// split deploys (e.g. Vercel frontend + Render backend).
const envBase = process.env.NEXT_PUBLIC_API_URL;
export const API_BASE =
  envBase !== undefined
    ? envBase
    : process.env.NODE_ENV === "development"
      ? "http://localhost:8000"
      : "";

export type Sentiment = {
  score: number;
  label: "bullish" | "bearish" | "neutral";
  magnitude: number;
};

export type NewsItem = {
  id: string;
  title: string;
  summary: string;
  link: string;
  source: string;
  published: string;
  sentiment: Sentiment;
  impact: number;
};

export type AgentRow = {
  id: string;
  name: string;
  role: string;
  strategy: string;
  risk: number;
  cash: number;
  position: number;
  pnl: number;
  trade_count: number;
  bias: number;
};

export type Decision = {
  agent_id: string;
  agent_name: string;
  agent_role: string;
  action: "buy" | "sell" | "hold";
  size: number;
  rationale: string;
};

export type TapePoint = {
  t: number;
  price: number;
  sentiment: number;
  event: string | null;
};

export type MarketState = {
  ticker: string;
  price: number;
  sentiment: number;
  trend: number;
  volatility: number;
  tape: TapePoint[];
};

export type SimResult = {
  simulation_id: number;
  event: {
    headline: string;
    summary: string;
    source: string;
    sentiment: number;
    magnitude: number;
  };
  market: MarketState;
  price_before: number;
  price_after: number;
  shock_pct: number;
  decisions: Decision[];
  narrative: string;
  agents: AgentRow[];
};

async function j<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${txt}`);
  }
  return res.json();
}

export const api = {
  news: (force = false) =>
    fetch(`${API_BASE}/api/news${force ? "/refresh" : ""}`, {
      cache: "no-store",
    }).then(j<{ count: number; items: NewsItem[] }>),

  state: () =>
    fetch(`${API_BASE}/api/simulation/state`, { cache: "no-store" }).then(
      j<{ market: MarketState; agents: AgentRow[] }>,
    ),

  agents: () =>
    fetch(`${API_BASE}/api/agents`, { cache: "no-store" }).then(
      j<{ agents: AgentRow[]; roles: string[] }>,
    ),

  addAgent: (body: {
    name: string;
    role: string;
    strategy?: string;
    risk?: number;
  }) =>
    fetch(`${API_BASE}/api/agents`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    }).then(j<AgentRow>),

  removeAgent: (id: string) =>
    fetch(`${API_BASE}/api/agents/${id}`, { method: "DELETE" }).then(
      j<{ ok: boolean }>,
    ),

  runEvent: (body: {
    headline: string;
    summary?: string;
    source?: string;
    sentiment?: number;
    magnitude?: number;
    news_id?: string;
  }) =>
    fetch(`${API_BASE}/api/simulation/event`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    }).then(j<SimResult>),

  reset: () =>
    fetch(`${API_BASE}/api/simulation/reset`, { method: "POST" }).then(
      j<{ ok: boolean }>,
    ),

  history: () =>
    fetch(`${API_BASE}/api/simulation/history`, { cache: "no-store" }).then(
      j<{ runs: any[] }>,
    ),
};
