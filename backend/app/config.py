from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "arena.db"

# Free RSS sources only. No keys, no trials.
NEWS_FEEDS = [
    ("Yahoo Finance",
     "https://finance.yahoo.com/news/rssindex"),
    ("Google News — Markets",
     "https://news.google.com/rss/search?q=stock+market+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Google News — Fed",
     "https://news.google.com/rss/search?q=federal+reserve+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CNBC — Top News",
     "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("CNBC — Markets",
     "https://www.cnbc.com/id/15839069/device/rss/rss.html"),
]

NEWS_CACHE_TTL_SECONDS = 120
NEWS_MAX_ITEMS = 60

# Market defaults
DEFAULT_TICKER = "SPX"
DEFAULT_PRICE = 4500.0
TAPE_MAX_LEN = 400
