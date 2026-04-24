# Agent Arena

AI-powered multi-agent simulation platform. Heterogeneous agents (retail traders,
hedge funds, quants, central banks) react to live financial news and each other
inside a simulated market, producing prices, sentiment and narratives you can
watch unfold in real time.

```
news (RSS) ──► sentiment ──► event bus ──► agents ──► orders ──► market ──► tape
                                   ▲                                │
                                   └────────────── feedback ◄───────┘
```

## Stack

- **Backend** — Python 3.10+, FastAPI, SQLite, `feedparser`, `httpx`.
- **Frontend** — Next.js 14 (App Router), TailwindCSS, Recharts.
- **Data** — 100% free RSS: Yahoo Finance, Google News (finance), CNBC.

## Repo layout

```
backend/
  app/
    agents/          heterogeneous agent implementations
    services/        news ingestion + sentiment
    simulation/      market, events, engine loop
    routes/          FastAPI routers
    main.py          app factory
frontend/
  app/               Next.js App Router pages
  components/        dashboard widgets
  lib/               API client
```

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API is then on `http://localhost:8000` (docs at `/docs`).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard on `http://localhost:3000`. It expects the backend on port 8000; override with `NEXT_PUBLIC_API_URL`.

## What you can do

- Pull live headlines from free RSS feeds and see them scored for sentiment.
- Click a headline to inject it into the arena — watch each agent react.
- Create a custom event ("Fed hikes 50bps", "AAPL beats earnings") and see
  price, sentiment and agent P&L respond.
- Add / remove agents, swap strategies (momentum, mean-reversion, risk-off,
  policy), and replay past simulation runs.

## API surface

| Method | Path                         | Purpose                                 |
| ------ | ---------------------------- | --------------------------------------- |
| GET    | `/api/news`                  | Latest RSS headlines + sentiment        |
| GET    | `/api/news/refresh`          | Force a refresh                         |
| GET    | `/api/agents`                | List active agents                      |
| POST   | `/api/agents`                | Add an agent                            |
| DELETE | `/api/agents/{id}`           | Remove an agent                         |
| POST   | `/api/simulation/event`      | Inject an event, get market+agent delta |
| GET    | `/api/simulation/state`      | Current market state + tape             |
| GET    | `/api/simulation/history`    | Past simulation runs                    |
| POST   | `/api/simulation/reset`      | Reset the arena                         |

## Notes

- No paid APIs. No keys required. No trials.
- SQLite file lives at `backend/arena.db` and is created on first run.
