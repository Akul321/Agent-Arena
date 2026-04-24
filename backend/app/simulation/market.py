"""Simulated market maker.

Price moves driven by (a) a shock from the incoming event and (b) net order
flow from the agents against a bounded market-impact function. Running
volatility + trend are maintained for agents to observe.
"""
from __future__ import annotations

import math
import random
import time
from collections import deque
from dataclasses import dataclass, field

from ..config import DEFAULT_PRICE, DEFAULT_TICKER, TAPE_MAX_LEN


@dataclass
class TapePoint:
    t: float
    price: float
    sentiment: float
    event: str | None = None


@dataclass
class Market:
    ticker: str = DEFAULT_TICKER
    price: float = DEFAULT_PRICE
    sentiment: float = 0.0
    tape: deque[TapePoint] = field(
        default_factory=lambda: deque(maxlen=TAPE_MAX_LEN)
    )

    def __post_init__(self) -> None:
        if not self.tape:
            self.tape.append(TapePoint(time.time(), self.price, 0.0, "open"))

    # ---- observables ----------------------------------------------------
    def trend(self) -> float:
        """Normalised log-return over the last ~20 points."""
        if len(self.tape) < 2:
            return 0.0
        window = list(self.tape)[-20:]
        start = window[0].price
        end = window[-1].price
        if start <= 0:
            return 0.0
        ret = math.log(end / start)
        return max(-1.0, min(1.0, ret * 50))

    def volatility(self) -> float:
        if len(self.tape) < 3:
            return 0.005
        window = list(self.tape)[-20:]
        rets = []
        for a, b in zip(window, window[1:]):
            if a.price > 0:
                rets.append(math.log(b.price / a.price))
        if not rets:
            return 0.005
        mean = sum(rets) / len(rets)
        var = sum((r - mean) ** 2 for r in rets) / len(rets)
        return math.sqrt(var)

    # ---- mutation -------------------------------------------------------
    def apply_shock(self, sentiment: float, magnitude: float) -> float:
        """Instantaneous reaction to a news event."""
        # Scale so a strong bullish headline (score ~1, mag ~1) moves ~0.8%.
        shock = sentiment * magnitude * 0.008
        # Sprinkle a little noise — markets are reflexive.
        shock += random.gauss(0, 0.0015)
        self.price *= 1 + shock
        # Blend event sentiment into running market sentiment.
        self.sentiment = max(-1.0, min(1.0, 0.7 * self.sentiment + 0.3 * sentiment * magnitude))
        return shock

    def apply_flow(self, net_shares: float) -> float:
        """Translate net agent order flow to a price move.

        Impact = tanh(flow / K) * 0.005 — bounded so a single round cannot
        dislocate the book by more than ~50 bps.
        """
        if net_shares == 0:
            return 0.0
        impact = math.tanh(net_shares / 1500.0) * 0.005
        self.price *= 1 + impact
        return impact

    def record(self, event: str | None = None) -> None:
        self.tape.append(TapePoint(
            t=time.time(),
            price=round(self.price, 4),
            sentiment=round(self.sentiment, 3),
            event=event,
        ))

    def snapshot_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "price": round(self.price, 4),
            "sentiment": round(self.sentiment, 3),
            "trend": round(self.trend(), 3),
            "volatility": round(self.volatility(), 4),
            "tape": [
                {
                    "t": p.t,
                    "price": p.price,
                    "sentiment": p.sentiment,
                    "event": p.event,
                }
                for p in self.tape
            ],
        }
