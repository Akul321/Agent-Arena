from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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


@app.get("/health")
def health() -> dict:
    return {"ok": True}


# Optional static UI. If the built frontend is present, serve it from "/".
# If not (e.g. plain `uvicorn` in dev), fall back to a JSON index so the API
# is still discoverable.
STATIC_DIR = Path(__file__).resolve().parent / "static"


if STATIC_DIR.is_dir() and (STATIC_DIR / "index.html").exists():

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    # `html=True` makes StaticFiles serve index.html for directory requests,
    # which matches the Next.js static export (trailingSlash: true).
    app.mount(
        "/",
        StaticFiles(directory=STATIC_DIR, html=True),
        name="static",
    )

else:

    @app.get("/")
    def root() -> dict:
        return {
            "name": "Agent Arena",
            "docs": "/docs",
            "endpoints": [
                "/api/news",
                "/api/news/refresh",
                "/api/news/top",
                "/api/agents",
                "/api/simulation/event",
                "/api/simulation/state",
                "/api/simulation/history",
                "/api/simulation/reset",
            ],
        }
