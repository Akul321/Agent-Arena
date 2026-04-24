"""Retail trader — noisy, sentiment-driven, chases momentum."""
from __future__ import annotations

import random

from .base import Agent, Decision, Event, MarketSnapshot


class RetailTrader(Agent):
    role = "Retail Trader"
    default_strategy = "momentum"

    def decide(self, snapshot: MarketSnapshot, event: Event) -> Decision:
        self.memory.observe(event)

        # Retail listens to headlines loudly and to the tape a little.
        score = 0.7 * event.sentiment * event.magnitude + 0.3 * snapshot.trend
        # FOMO kicker when the headline and tape agree.
        if score * snapshot.trend > 0:
            score *= 1.2
        # Noise — retail is noisy.
        score += random.uniform(-0.15, 0.15)

        if abs(score) < 0.1:
            return Decision(
                self.id, self.name, self.role, "hold", 0.0,
                "Waiting for a cleaner signal.",
            )

        action = "buy" if score > 0 else "sell"
        size = round(self.risk * 80 * min(1.0, abs(score) + 0.2), 2)
        if action == "sell":
            size = min(size, max(self.position, size * 0.5))

        rationale = (
            f"Headline reads {event.sentiment:+.2f}; tape trending "
            f"{snapshot.trend:+.2f}. Going with the crowd."
        )
        return Decision(self.id, self.name, self.role, action, size, rationale)
