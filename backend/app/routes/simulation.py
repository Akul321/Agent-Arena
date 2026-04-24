from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..agents.base import Event
from ..services.news_service import news_service
from ..services.sentiment import score as score_text
from ..simulation.engine import arena


router = APIRouter(prefix="/api/simulation", tags=["simulation"])


class EventIn(BaseModel):
    headline: str = Field(min_length=3, max_length=280)
    summary: str = ""
    source: str = "user"
    sentiment: float | None = None   # if omitted, scored from text
    magnitude: float | None = None
    news_id: str | None = None


@router.post("/event")
async def inject_event(payload: EventIn) -> dict:
    event = await _materialise(payload)
    return arena.run_event(event)


@router.get("/state")
def current_state() -> dict:
    return arena.state()


@router.get("/history")
def history(limit: int = 25) -> dict:
    return {"runs": arena.history(limit=limit)}


@router.post("/reset")
def reset() -> dict:
    arena.reset()
    return {"ok": True, **arena.state()}


async def _materialise(payload: EventIn) -> Event:
    if payload.news_id:
        # Make sure cache is warm, then look up.
        await news_service.get()
        item = news_service.find(payload.news_id)
        if not item:
            raise HTTPException(status_code=404, detail="news_id not found")
        return Event(
            headline=item.title,
            summary=item.summary,
            source=item.source,
            sentiment=item.sentiment.get("score", 0.0),
            magnitude=item.sentiment.get("magnitude", 0.5),
            tags=["news"],
        )

    text = f"{payload.headline}. {payload.summary}"
    scored = score_text(text)
    return Event(
        headline=payload.headline,
        summary=payload.summary,
        source=payload.source,
        sentiment=payload.sentiment if payload.sentiment is not None else scored.score,
        magnitude=payload.magnitude if payload.magnitude is not None else max(0.35, scored.magnitude),
        tags=["user"],
    )
