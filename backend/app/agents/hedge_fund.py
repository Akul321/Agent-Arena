"""Hedge fund — larger size, scales into conviction, fades extremes."""
from __future__ import annotations

from .base import Agent, Decision, Event, MarketSnapshot


class HedgeFund(Agent):
    role = "Hedge Fund"
    default_strategy = "directional"

    def decide(self, snapshot: MarketSnapshot, event: Event) -> Decision:
        self.memory.observe(event)

        bias = self.memory.cumulative_sentiment
        signal = 0.5 * event.sentiment * event.magnitude + 0.3 * bias + 0.2 * snapshot.trend

        # Fade melt-ups / capitulations: if volatility is high and the crowd
        # is all one way, lean the other way a bit.
        if snapshot.volatility > 0.02 and snapshot.sentiment * signal > 0.5:
            signal *= 0.5

        if abs(signal) < 0.12:
            return Decision(
                self.id, self.name, self.role, "hold", 0.0,
                "Signal inside our noise band.",
            )

        action = "buy" if signal > 0 else "sell"
        # Hedge funds size up with conviction, capped by risk budget.
        size = round(self.risk * 400 * min(1.0, abs(signal)), 2)
        if action == "sell":
            size = max(size, 50.0)  # willing to short

        rationale = (
            f"Composite signal {signal:+.2f} (news {event.sentiment:+.2f}, "
            f"bias {bias:+.2f}, tape {snapshot.trend:+.2f})."
        )
        return Decision(self.id, self.name, self.role, action, size, rationale)
