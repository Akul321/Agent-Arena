"""Quant — statistical, mean-reverting, ignores narrative."""
from __future__ import annotations

import math

from .base import Agent, Decision, Event, MarketSnapshot


class QuantAgent(Agent):
    role = "Quant"
    default_strategy = "mean_reversion"

    def decide(self, snapshot: MarketSnapshot, event: Event) -> Decision:
        self.memory.observe(event)

        # Z-score of recent trend — fade extremes.
        vol = max(1e-4, snapshot.volatility)
        z = snapshot.trend / vol
        signal = -math.tanh(z / 8)

        # Tiny tilt from news in case of genuine regime shift.
        signal += 0.1 * event.sentiment * event.magnitude

        if abs(signal) < 0.15:
            return Decision(
                self.id, self.name, self.role, "hold", 0.0,
                f"z={z:+.2f}, inside band.",
            )

        action = "buy" if signal > 0 else "sell"
        size = round(self.risk * 250 * min(1.0, abs(signal)), 2)
        rationale = (
            f"Mean-reversion: tape z={z:+.2f}, fading with signal {signal:+.2f}."
        )
        return Decision(self.id, self.name, self.role, action, size, rationale)
