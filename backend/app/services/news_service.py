"""RSS news ingestion. Free sources only."""
from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from typing import Iterable

import feedparser
import httpx

from ..config import NEWS_CACHE_TTL_SECONDS, NEWS_FEEDS, NEWS_MAX_ITEMS
from . import sentiment


@dataclass
class NewsItem:
    id: str
    title: str
    summary: str
    link: str
    source: str
    published: str  # ISO-8601
    published_ts: float
    sentiment: dict = field(default_factory=dict)
    impact: float = 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "link": self.link,
            "source": self.source,
            "published": self.published,
            "sentiment": self.sentiment,
            "impact": round(self.impact, 3),
        }


def _strip_html(text: str) -> str:
    import re
    no_tags = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"\s+", " ", no_tags).strip()


def _entry_id(entry) -> str:
    raw = entry.get("id") or entry.get("link") or entry.get("title") or ""
    return hashlib.sha1(raw.encode("utf-8", "ignore")).hexdigest()[:16]


def _entry_ts(entry) -> float:
    tm = entry.get("published_parsed") or entry.get("updated_parsed")
    if tm:
        return time.mktime(tm)
    return time.time()


def _entry_iso(ts: float) -> str:
    import datetime as dt
    return dt.datetime.utcfromtimestamp(ts).isoformat() + "Z"


class NewsService:
    def __init__(self) -> None:
        self._cache: list[NewsItem] = []
        self._last_fetch: float = 0.0
        self._lock = asyncio.Lock()

    async def get(self, force: bool = False) -> list[NewsItem]:
        if not force and self._cache and (
            time.time() - self._last_fetch < NEWS_CACHE_TTL_SECONDS
        ):
            return self._cache
        async with self._lock:
            if not force and self._cache and (
                time.time() - self._last_fetch < NEWS_CACHE_TTL_SECONDS
            ):
                return self._cache
            self._cache = await self._fetch_all()
            self._last_fetch = time.time()
        return self._cache

    async def _fetch_all(self) -> list[NewsItem]:
        async with httpx.AsyncClient(
            timeout=8.0,
            headers={"User-Agent": "AgentArena/1.0 (+https://localhost)"},
            follow_redirects=True,
        ) as client:
            results = await asyncio.gather(
                *[self._fetch_feed(client, src, url) for src, url in NEWS_FEEDS],
                return_exceptions=True,
            )
        items: list[NewsItem] = []
        seen: set[str] = set()
        for r in results:
            if isinstance(r, Exception):
                continue
            for item in r:
                if item.id in seen:
                    continue
                seen.add(item.id)
                items.append(item)
        items.sort(key=lambda i: i.published_ts, reverse=True)
        items = items[:NEWS_MAX_ITEMS]
        self._score(items)
        return items

    async def _fetch_feed(
        self, client: httpx.AsyncClient, source: str, url: str
    ) -> list[NewsItem]:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            parsed = feedparser.parse(resp.content)
        except Exception:
            return []

        out: list[NewsItem] = []
        for entry in parsed.entries[:25]:
            title = _strip_html(entry.get("title", "")).strip()
            if not title:
                continue
            summary = _strip_html(entry.get("summary", "") or entry.get("description", ""))
            ts = _entry_ts(entry)
            out.append(NewsItem(
                id=_entry_id(entry),
                title=title,
                summary=summary[:360],
                link=entry.get("link", ""),
                source=source,
                published=_entry_iso(ts),
                published_ts=ts,
            ))
        return out

    @staticmethod
    def _score(items: Iterable[NewsItem]) -> None:
        now = time.time()
        for item in items:
            text = f"{item.title}. {item.summary}"
            result = sentiment.score(text)
            item.sentiment = result.to_dict()
            age_hours = max(0.0, (now - item.published_ts) / 3600.0)
            recency = max(0.1, 1.0 - age_hours / 24.0)
            item.impact = abs(result.score) * result.magnitude * recency

    def find(self, news_id: str) -> NewsItem | None:
        for item in self._cache:
            if item.id == news_id:
                return item
        return None


news_service = NewsService()
