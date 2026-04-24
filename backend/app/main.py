from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .routes import agents as agents_route
from .routes import news as news_route
from .routes import simulation as sim_route


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Agent Arena API",
    description="Multi-agent financial simulation fed by free RSS news.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_route.router)
app.include_router(agents_route.router)
app.include_router(sim_route.router)


@app.get("/")
def root() -> dict:
    return {
        "name": "Agent Arena",
        "docs": "/docs",
        "endpoints": [
            "/api/news", "/api/news/refresh", "/api/news/top",
            "/api/agents",
            "/api/simulation/event", "/api/simulation/state",
            "/api/simulation/history", "/api/simulation/reset",
        ],
    }


@app.get("/health")
def health() -> dict:
    return {"ok": True}
