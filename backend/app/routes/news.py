from fastapi import APIRouter

from ..services.news_service import news_service


router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("")
async def list_news() -> dict:
    items = await news_service.get()
    return {
        "count": len(items),
        "items": [i.to_dict() for i in items],
    }


@router.get("/refresh")
async def refresh() -> dict:
    items = await news_service.get(force=True)
    return {"count": len(items), "items": [i.to_dict() for i in items]}


@router.get("/top")
async def top(limit: int = 10) -> dict:
    items = await news_service.get()
    ranked = sorted(items, key=lambda i: i.impact, reverse=True)[:limit]
    return {"items": [i.to_dict() for i in ranked]}
