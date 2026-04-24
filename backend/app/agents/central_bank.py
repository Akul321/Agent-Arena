"""Central bank — rarely trades, but leans against extremes. Sets policy bias."""
from __future__ import annotations

from .base import Agent, Decision, Event, MarketSnapshot


class CentralBank(Agent):
    role = "Central Bank"
    default_strategy = "policy"

    POLICY_KEYWORDS = (
        "fed", "federal reserve", "rate", "hike", "cut", "inflation",
        "cpi", "pce", "fomc", "powell", "ecb", "boj", "boe",
    )

    def decide(self, snapshot: MarketSnapshot, event: Event) -> Decision:
        self.memory.observe(event)

        text = f"{event.headline} {event.summary}".lower()
        is_policy = any(k in text for k in self.POLICY_KEYWORDS)

        # Extreme moves trigger intervention.
        extreme = abs(snapshot.trend) > 0.8 or abs(snapshot.sentiment) > 0.7

        if not is_policy and not extreme:
            return Decision(
                self.id, self.name, self.role, "hold", 0.0,
                "No mandate to act.",
            )

        # Lean against the wind.
        direction = -1.0 if snapshot.trend > 0 else 1.0
        conviction = 0.5 if is_policy else 0.3
        if extreme:
            conviction += 0.3

        action = "buy" if direction > 0 else "sell"
        size = round(self.risk * 600 * conviction, 2)

        rationale = (
            "Policy response — leaning against the wind."
            if is_policy else
            "Stabilising: tape disordered, intervening."
        )
        return Decision(self.id, self.name, self.role, action, size, rationale)
