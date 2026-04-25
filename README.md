# Agent Arena

> Multi-agent market simulation. Heterogeneous agents — retail traders, hedge
> funds, quants, a central bank — react to live financial news and to each
> other inside a simulated market, producing prices, sentiment and narratives
> you can watch unfold in real time.

## 🚀 Live demo

| Host | What lives there | URL |
| ---- | ---------------- | --- |
| Render (full app) | Backend + UI in one container | <!-- RENDER_URL --> _add after first deploy_ |
| Vercel (UI only)  | Frontend, talking to the Render backend | <!-- VERCEL_URL --> _add after first deploy_ |

Click either button below to spin up your own copy. No credit card, no keys.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Akul321/Agent-Arena)
&nbsp;
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FAkul321%2FAgent-Arena&root-directory=frontend&project-name=agent-arena&env=NEXT_PUBLIC_API_URL&envDescription=URL%20of%20the%20Agent%20Arena%20backend%20(Render)&envLink=https%3A%2F%2Fgithub.com%2FAkul321%2FAgent-Arena%23deploy)

```
news (RSS) ──► sentiment ──► event bus ──► agents ──► orders ──► market ──► tape
                                   ▲                                │
                                   └────────────── feedback ◄───────┘
```

## What you can do

- Pull live headlines from free RSS feeds (Yahoo Finance, Google News, CNBC),
  ranked by sentiment + recency.
- Click a headline to inject it into the arena and watch each agent react.
- Type a custom event ("Fed cuts rates", "AAPL beats earnings") and see
  price, sentiment and agent P&L respond.
- Add / remove agents, swap strategies (momentum, mean-reversion, risk-off,
  policy), tune their risk budget.
- Replay any past simulation with full per-agent reasoning.

## Tech

- **Backend** — Python 3.11, FastAPI, SQLite, `feedparser`, `httpx`.
- **Frontend** — Next.js 14 (App Router, static export), TailwindCSS, Recharts.
- **Packaging** — single Docker image; FastAPI serves the built UI at `/`
  and the JSON API under `/api/*`. Same image works on Render, Fly, Railway,
  Cloud Run, your own VM.
- **Data** — 100% free RSS. No keys, no trials, no credit card.

## Repo layout

```
Dockerfile              builds frontend, then copies into backend image
render.yaml             Render blueprint (free tier, Docker)
backend/
  app/
    agents/             heterogeneous agent implementations
    services/           news ingestion + sentiment
    simulation/         market, events, engine loop
    routes/             FastAPI routers
    main.py             app factory; serves static UI when present
frontend/
  app/                  Next.js App Router pages
  components/           dashboard widgets
  lib/                  API client
  next.config.mjs       output: "export" → static site
  vercel.json           Vercel project config
```

## Deploy

### Option A — one-click Render (full app, single URL)

1. Click **Deploy to Render** above.
2. Sign in with GitHub (free, no card). Render reads `render.yaml`, builds the
   `Dockerfile`, gives you `https://agent-arena-<hash>.onrender.com`.
3. Open that URL — backend + dashboard are both there.

### Option B — split deploy (Vercel UI + Render backend)

Faster UI delivery (Vercel CDN), API still on Render.

1. **Backend on Render** — same as Option A. Note the resulting URL, e.g.
   `https://agent-arena-api.onrender.com`.
2. **Frontend on Vercel** — click **Deploy with Vercel** above. Vercel asks
   for `NEXT_PUBLIC_API_URL`; paste the Render URL from step 1. Vercel sets
   the root directory to `frontend/` automatically.
3. Open the Vercel URL — it'll be `https://agent-arena-<hash>.vercel.app`.

### Option C — Docker, anywhere

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

API on `http://localhost:8000` (interactive docs at `/docs`).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard on `http://localhost:3000`. In dev it talks to the backend on port
8000 by default. Override with `NEXT_PUBLIC_API_URL` if you moved it.

## API surface

| Method | Path                         | Purpose                                 |
| ------ | ---------------------------- | --------------------------------------- |
| GET    | `/api/news`                  | Latest RSS headlines + sentiment        |
| GET    | `/api/news/refresh`          | Force a refresh                         |
| GET    | `/api/news/top`              | Top N by computed impact                |
| GET    | `/api/agents`                | List active agents + available roles    |
| POST   | `/api/agents`                | Add an agent                            |
| DELETE | `/api/agents/{id}`           | Remove an agent                         |
| POST   | `/api/simulation/event`      | Inject an event, get market+agent delta |
| GET    | `/api/simulation/state`      | Current market state + tape             |
| GET    | `/api/simulation/history`    | Past simulation runs                    |
| POST   | `/api/simulation/reset`      | Reset the arena                         |
| GET    | `/health`                    | Health check (used by container probes) |

## Notes

- SQLite lives at `backend/arena.db` and is created on first run. On Render's
  free tier the disk is ephemeral, so history resets across deploys — fine
  for a demo.
- `feedparser` is the RSS layer; some upstreams occasionally rate-limit.
  The service caches results for 2 minutes and gracefully ignores feed errors.
- The sentiment scorer is deliberately lightweight (lexicon + finance
  bigrams). Strong enough to move the simulation; not a substitute for an
  LLM if you want nuance.
- Vercel-hosted UI relies on the Render backend allowing CORS — the FastAPI
  app sets `allow_origins=["*"]`, so it works out of the box.
