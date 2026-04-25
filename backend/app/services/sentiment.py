"""Lexicon-based sentiment scoring.

Deliberately lightweight — no model downloads, no API keys. Returns a score
in [-1, 1] plus a label. Accurate enough to move a simulated market and to
sort headlines by impact.

Two passes:
  1. Phrase matcher for finance-specific bigrams/trigrams (rate cuts,
     earnings beat, inflation cools, etc.). These dominate.
  2. Token matcher with intensifier weights and simple negation.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass


# Phrase-level signals — finance has lots of bigrams that flip a token's
# default polarity. (e.g. "cut" alone is negative, "rate cut" is bullish.)
PHRASES: list[tuple[str, float]] = [
    # Monetary policy — easing is bullish, tightening is bearish.
    ("rate cut", +1.4),
    ("rate cuts", +1.4),
    ("cut rates", +1.4),
    ("cuts rates", +1.4),
    ("cutting rates", +1.4),
    ("dovish", +1.0),
    ("rate hike", -1.4),
    ("rate hikes", -1.4),
    ("hike rates", -1.4),
    ("hikes rates", -1.4),
    ("hawkish", -1.0),
    ("inflation cools", +1.0),
    ("inflation eases", +1.0),
    ("inflation slows", +1.0),
    ("inflation rises", -1.0),
    ("inflation surges", -1.2),
    ("inflation hot", -0.9),
    # Earnings
    ("beats earnings", +1.3),
    ("earnings beat", +1.3),
    ("crushes earnings", +1.5),
    ("misses earnings", -1.3),
    ("earnings miss", -1.3),
    ("guidance raised", +1.2),
    ("raises guidance", +1.2),
    ("guidance cut", -1.2),
    ("cuts guidance", -1.2),
    ("slashes outlook", -1.4),
    ("record profits", +1.2),
    ("record earnings", +1.2),
    # Risk-off
    ("flight to safety", -1.0),
    ("risk off", -0.9),
    ("risk on", +0.9),
    ("soft landing", +1.0),
    ("hard landing", -1.2),
]

POSITIVE_WORDS = {
    "beat", "beats", "surge", "surges", "soar", "soars", "rally", "rallies",
    "jump", "jumps", "gain", "gains", "rise", "rises", "climb", "climbs",
    "record", "strong", "robust", "upbeat", "bullish", "outperform",
    "upgrade", "upgraded", "profit", "profits", "boost", "boosts",
    "breakthrough", "expansion", "accelerate", "recover", "recovers",
    "optimistic", "confidence", "deal", "agreement", "dividend", "rebound",
    "resilient", "ease", "eases", "cools", "stimulus",
}

NEGATIVE_WORDS = {
    "miss", "misses", "plunge", "plunges", "slump", "slumps", "crash",
    "crashes", "drop", "drops", "fall", "falls", "slide", "slides",
    "tumble", "tumbles", "decline", "declines", "loss", "losses",
    "downgrade", "downgraded", "weak", "warn", "warns", "warning",
    "bearish", "fear", "fears", "panic", "recession", "default",
    "bankruptcy", "layoff", "layoffs", "probe", "lawsuit",
    "fraud", "scandal", "shutdown", "sanctions", "strike", "selloff",
    "tariff", "tariffs",
}

INTENSIFIERS = {
    "surge": 1.5, "plunge": 1.5, "crash": 1.8, "soar": 1.6,
    "record": 1.3, "panic": 1.7, "default": 1.6, "fraud": 1.8,
    "recession": 1.5, "bankruptcy": 1.8, "breakthrough": 1.4,
}

_TOKEN_RE = re.compile(r"[A-Za-z']+")


@dataclass
class SentimentResult:
    score: float   # -1..1
    label: str     # "bullish" | "bearish" | "neutral"
    magnitude: float  # 0..1, how strongly opinionated

    def to_dict(self) -> dict:
        return {
            "score": round(self.score, 3),
            "label": self.label,
            "magnitude": round(self.magnitude, 3),
        }


def score(text: str) -> SentimentResult:
    if not text:
        return SentimentResult(0.0, "neutral", 0.0)

    lower = text.lower()
    pos = neg = 0.0

    # Pass 1: phrases dominate.
    for phrase, weight in PHRASES:
        if phrase in lower:
            if weight > 0:
                pos += weight
            else:
                neg += -weight

    tokens = [t.lower() for t in _TOKEN_RE.findall(text)]
    if not tokens and pos == 0 and neg == 0:
        return SentimentResult(0.0, "neutral", 0.0)

    # Pass 2: tokens with negation window.
    for i, tok in enumerate(tokens):
        weight = INTENSIFIERS.get(tok, 1.0)
        negated = i > 0 and tokens[i - 1] in {"not", "no", "never"}
        if tok in POSITIVE_WORDS:
            if negated:
                neg += weight
            else:
                pos += weight
        elif tok in NEGATIVE_WORDS:
            if negated:
                pos += weight
            else:
                neg += weight

    total = pos + neg
    if total == 0:
        return SentimentResult(0.0, "neutral", 0.0)

    raw = (pos - neg) / total
    magnitude = 1 - math.exp(-total / 3)
    final = raw * magnitude

    if final > 0.15:
        label = "bullish"
    elif final < -0.15:
        label = "bearish"
    else:
        label = "neutral"

    return SentimentResult(score=final, label=label, magnitude=magnitude)
