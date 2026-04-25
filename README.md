# Agent Arena

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Akul321/Agent-Arena)

AI-powered multi-agent simulation platform. Heterogeneous agents — retail
traders, hedge funds, quants, a central bank — react to live financial news
and to each other inside a simulated market, producing prices, sentiment and
narratives you can watch unfold in real time.

```
news (RSS) ──► sentiment ──► event bus ──► agents ──► orders ──► market ──► tape
                                   ▲                                │
                                   └────────────── feedback ◄───────┘
```

## Live demo

After clicking the button above, Render builds the Docker image and gives you
a public URL like `https://agent-arena.onrender.com`. 
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
  and the JSON API under `/api/*`.
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
```

## Deploy

### Option A — one-click on Render (recommended)

1. Click the **Deploy to Render** button above (or push your fork to GitHub
   and create a new Web Service from the blueprint).
2. Render reads `render.yaml`, builds the `Dockerfile`, and exposes
   `https://<service>.onrender.com`.
3. Open the URL — backend + dashboard are both there.

### Option B — Docker, anywhere

```bash
docker build -t agent-arena .
docker run --rm -p 8000:8000 agent-arena
# open http://localhost:8000
```

Works on Fly.io, Railway, Google Cloud Run, your own VM — anywhere that
runs containers and exposes one port.

### Option C — split deploy (Vercel + Render)

If you'd rather host the UI on Vercel and the API on Render:

1. Deploy `backend/` only to Render (point its blueprint at `backend/Dockerfile`,
   or write a thin `render.yaml`).
2. Set `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com` in Vercel's
   project env.
3. Deploy `frontend/` to Vercel.

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
