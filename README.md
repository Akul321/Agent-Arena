# Agent Arena

Multi-agent market simulation. Heterogeneous agents — retail traders, hedge
funds, quants, a central bank — react to live financial news and to each
other inside a simulated market. Prices, sentiment and per-agent reasoning
unfold in real time on a Bloomberg-style dashboard.

## Live demo

| Host | What lives there | URL |
| ---- | ---------------- | --- |
| Render | Backend + UI in one container | <https://agent-arena-yl7l.onrender.com> |
| Vercel | Frontend on the CDN, talking to the Render backend | <https://agent-arena-beta.vercel.app> |

Render's free tier sleeps after ~15 minutes of inactivity, so the first
request after a quiet period takes ~30 seconds to wake up. Subsequent
requests are instant.

## Architecture

```
news (RSS) ──► sentiment ──► event bus ──► agents ──► orders ──► market ──► tape
                                   ▲                                │
                                   └────────────── feedback ◄───────┘
```

A single round of the simulation:

1. An event arrives — either a clicked headline, a typed prompt, or an
   automatic poll of the RSS feeds.
2. The sentiment service scores it on `[-1, +1]` and assigns a magnitude
   on `[0, 1]`.
3. The market applies the shock: `price *= 1 + sentiment * magnitude * 0.008 + N(0, 0.0015)`.
4. Each agent observes the post-shock snapshot (price, trend, vol, running
   sentiment) plus the event itself, runs its strategy, and emits a
   `(action, size, rationale)` decision.
5. Net order flow is folded back into the price with a bounded impact
   function: `price *= 1 + tanh(net_shares / 1500) * 0.005`. A single round
   cannot dislocate the book by more than ~50 bps.
6. Cash, position and P&L are settled per agent. The whole tick is appended
   to the tape and persisted to SQLite for replay.

## Agents

All four roles inherit from `Agent` (`backend/app/agents/base.py`), which
owns cash, position, P&L bookkeeping and a small `AgentMemory` of recent
events. Strategies differ in how they react to the same observation.

| Role | Strategy | Reads | Reacts to |
| ---- | -------- | ----- | --------- |
| Retail Trader | Momentum + sentiment chasing. Aggressive on strong headlines, prone to FOMO and stop-outs. | trend, event sentiment | latest headline |
| Hedge Fund | Macro thesis. Sizes up when news aligns with running sentiment; fades extreme moves. | trend, vol, running sentiment | regime shifts |
| Quant | Mean reversion against short-window trend; ignores narrative. | trend, vol | price dislocation |
| Central Bank | Policy stance. Sells (tightens) into hot inflation prints, buys (eases) into growth scares. Asymmetric and slow. | running sentiment, event keywords | policy-relevant events |

Each agent exposes a `risk_budget` you can tune from the dashboard. Agents
can be added, removed or duplicated at runtime.

## News + sentiment

`backend/app/services/news_service.py` polls three free RSS feeds (Yahoo
Finance, Google News finance, CNBC), de-duplicates on URL, and caches the
merged set for 2 minutes. No API keys, no quotas.

`backend/app/services/sentiment.py` runs a two-pass scorer:

1. **Phrase pass** — finance-specific bigrams (`"rate cut"`, `"earnings beat"`,
   `"dovish"`, `"hawkish"`, `"guidance lower"`, …) match first and dominate.
   Without this, "Fed signals rate cuts as inflation cools" scores bearish
   because both *cuts* and *inflation* are negative tokens in isolation.
2. **Token pass** — a small lexicon scores any remaining content.

Output is `(sentiment ∈ [-1, 1], magnitude ∈ [0, 1])`. Strong enough to
move the simulation; deliberately not an LLM.

## Market

`backend/app/simulation/market.py` keeps `price`, `sentiment`, a rolling
tape (capped, `deque(maxlen=…)`) and derived observables:

- `trend()` — log-return over the last 20 ticks, clipped to `[-1, 1]`.
- `volatility()` — rolling stdev of log-returns.
- `apply_shock(sentiment, magnitude)` — instantaneous news reaction.
- `apply_flow(net_shares)` — bounded order-flow impact (`tanh`-saturated).

## Tech stack

- **Backend** — Python 3.11, FastAPI, Pydantic, SQLite, `feedparser`, `httpx`.
- **Frontend** — Next.js 14 (App Router, static export), TailwindCSS, Recharts.
- **Container** — single Docker image. FastAPI serves the built UI at `/`
  and the JSON API under `/api/*`. Identical image runs on Render, Fly,
  Railway, Cloud Run, or your own VM.
- **Data** — 100% free RSS. No keys, no trials, no credit card.

## Repo layout

```
Dockerfile              two-stage build: Node frontend → Python backend
render.yaml             Render blueprint (free Docker tier)
backend/
  app/
    agents/             base.py + 4 role-specific strategies + factory
    services/           news_service.py, sentiment.py
    simulation/         market.py, engine.py (Arena orchestrator)
    routes/             FastAPI routers (news, agents, simulation)
    config.py           tunables: tickers, tape length, defaults
    main.py             app factory; mounts static UI when present
  requirements.txt
frontend/
  app/                  Next.js App Router pages
  components/           Header, NewsFeed, AgentPanel, MarketChart, EventPanel, HistoryPanel
  lib/api.ts            typed API client; reads NEXT_PUBLIC_API_URL
  next.config.mjs       output: "export" → static site
  vercel.json           Vercel project config (static build, framework=null)
```

## Deploy

### Render — full app, single URL

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Akul321/Agent-Arena)

Click the button, sign in with GitHub, accept the blueprint. Render reads
`render.yaml`, builds the `Dockerfile`, gives you one URL hosting both API
and dashboard. ~5 minutes to first deploy.

### Vercel — UI only, talks to the Render backend

Manual import (recommended over the deploy button, which would clone the
repo into your account):

1. Vercel → **Add New → Project → Import Git Repository** → pick this repo.
2. Set **Root Directory** to `frontend`.
3. Add env var `NEXT_PUBLIC_API_URL` = your Render URL (e.g.
   `https://agent-arena-yl7l.onrender.com`).
4. Deploy. Vercel serves the static export from `out/`.

### Docker, anywhere

```bash
docker build -t agent-arena .
docker run --rm -p 8000:8000 agent-arena
# open http://localhost:8000
```

## Local development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API on `http://localhost:8000`, interactive docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard on `http://localhost:3000`. By default it talks to
`http://localhost:8000`. Override with `NEXT_PUBLIC_API_URL`.

## API

| Method | Path                         | Purpose                                 |
| ------ | ---------------------------- | --------------------------------------- |
| GET    | `/api/news`                  | Latest RSS headlines + sentiment        |
| GET    | `/api/news/refresh`          | Force a refresh (bypass cache)          |
| GET    | `/api/news/top?n=`           | Top N by computed impact                |
| GET    | `/api/agents`                | List active agents + available roles    |
| POST   | `/api/agents`                | Add an agent `{role, name?, risk?}`     |
| DELETE | `/api/agents/{id}`           | Remove an agent                         |
| POST   | `/api/simulation/event`      | Inject an event, get market+agent delta |
| GET    | `/api/simulation/state`      | Current market state + tape             |
| GET    | `/api/simulation/history`    | Past simulation runs                    |
| POST   | `/api/simulation/reset`      | Reset the arena                         |
| GET    | `/health`                    | Liveness probe                          |

## Configuration

| Variable              | Where        | Default                                    | Effect |
| --------------------- | ------------ | ------------------------------------------ | ------ |
| `PORT`                | backend      | `8000`                                     | uvicorn bind port |
| `NEXT_PUBLIC_API_URL` | frontend     | `http://localhost:8000` (dev), `""` (prod) | Backend base URL the UI calls |
| `DEFAULT_TICKER`      | `config.py`  | `ARENA`                                    | Synthetic ticker label |
| `DEFAULT_PRICE`       | `config.py`  | `100.0`                                    | Opening price |
| `TAPE_MAX_LEN`        | `config.py`  | `500`                                      | Rolling tape length |

## Notes

- SQLite lives at `backend/arena.db` and is created on first run. Render's
  free disk is ephemeral, so history resets across deploys — fine for a demo.
- `feedparser` upstreams occasionally rate-limit. The service caches for
  2 minutes and ignores feed errors silently rather than failing the page.
- The FastAPI app sets `allow_origins=["*"]`, so a Vercel-hosted UI can
  call the Render backend without further config.
