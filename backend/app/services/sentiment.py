"""Lexicon-based sentiment scoring.

Deliberately lightweight — no model downloads, no API keys. Returns a score
in [-1, 1] plus a label. Accurate enough to move a simulated market and to
sort headlines by impact.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass


POSITIVE_WORDS = {
    "beat", "beats", "surge", "surges", "soar", "soars", "rally", "rallies",
    "jump", "jumps", "gain", "gains", "rise", "rises", "climb", "climbs",
    "record", "strong", "robust", "upbeat", "bullish", "outperform",
    "upgrade", "upgraded", "profit", "profits", "boost", "boosts",
    "breakthrough", "expansion", "accelerate", "recover", "recovers",
    "optimistic", "confidence", "deal", "agreement", "dividend",
}

NEGATIVE_WORDS = {
    "miss", "misses", "plunge", "plunges", "slump", "slumps", "crash",
    "crashes", "drop", "drops", "fall", "falls", "slide", "slides",
    "tumble", "tumbles", "decline", "declines", "loss", "losses",
    "downgrade", "downgraded", "weak", "warn", "warns", "warning",
    "bearish", "fear", "fears", "panic", "recession", "default",
    "bankruptcy", "layoff", "layoffs", "cut", "cuts", "probe", "lawsuit",
    "fraud", "scandal", "shutdown", "sanctions", "strike", "selloff",
    "inflation", "hike", "hikes",
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

    tokens = [t.lower() for t in _TOKEN_RE.findall(text)]
    if not tokens:
        return SentimentResult(0.0, "neutral", 0.0)

    pos = neg = 0.0
    for i, tok in enumerate(tokens):
        weight = INTENSIFIERS.get(tok, 1.0)
        # Simple negation window: "not good" flips.
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
