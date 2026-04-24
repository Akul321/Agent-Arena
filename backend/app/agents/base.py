"""Base agent contracts.

An agent observes (market snapshot + event) and returns a Decision. Agents are
stateful — they carry memory, cash, position and a running P&L. The simulation
engine is responsible for settling trades against the market maker.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Literal


Action = Literal["buy", "sell", "hold"]


@dataclass
class MarketSnapshot:
    price: float
    trend: float         # short-term momentum, roughly in [-1, 1]
    volatility: float    # recent realised vol, >= 0
    sentiment: float     # rolling market sentiment in [-1, 1]


@dataclass
class Event:
    headline: str
    summary: str = ""
    source: str = "user"
    sentiment: float = 0.0
    magnitude: float = 0.0  # 0..1
    tags: list[str] = field(default_factory=list)


@dataclass
class Decision:
    agent_id: str
    agent_name: str
    agent_role: str
    action: Action
    size: float           # in shares / contracts
    rationale: str


@dataclass
class AgentMemory:
    """Short-term (last N events) + long-term (aggregate bias)."""
    recent_events: list[Event] = field(default_factory=list)
    cumulative_sentiment: float = 0.0
    trade_count: int = 0

    def observe(self, event: Event) -> None:
        self.recent_events.append(event)
        if len(self.recent_events) > 8:
            self.recent_events.pop(0)
        self.cumulative_sentiment = 0.9 * self.cumulative_sentiment + 0.1 * event.sentiment


class Agent:
    """Abstract agent. Subclasses implement :meth:`decide`."""
    role: str = "Generic"
    default_strategy: str = "discretionary"

    def __init__(
        self,
        name: str,
        strategy: str | None = None,
        risk: float = 0.5,
        cash: float = 1_000_000.0,
    ) -> None:
        self.id = uuid.uuid4().hex[:8]
        self.name = name
        self.strategy = strategy or self.default_strategy
        self.risk = max(0.05, min(1.0, risk))
        self.cash = cash
        self.position = 0.0
        self.avg_entry = 0.0
        self.pnl = 0.0
        self.memory = AgentMemory()

    # ---- subclass API ---------------------------------------------------
    def decide(self, snapshot: MarketSnapshot, event: Event) -> Decision:
        raise NotImplementedError

    # ---- book-keeping ---------------------------------------------------
    def settle(self, action: Action, size: float, price: float) -> None:
        if action == "buy" and size > 0:
            new_pos = self.position + size
            # Weighted average entry for the current long book.
            if self.position >= 0 and new_pos > 0:
                self.avg_entry = (
                    self.avg_entry * self.position + price * size
                ) / new_pos
            self.position = new_pos
            self.cash -= size * price
            self.memory.trade_count += 1
        elif action == "sell" and size > 0:
            self.position -= size
            self.cash += size * price
            self.memory.trade_count += 1

    def mark(self, price: float) -> None:
        realised = self.cash - 1_000_000.0
        unrealised = self.position * price
        self.pnl = realised + unrealised

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "strategy": self.strategy,
            "risk": self.risk,
            "cash": round(self.cash, 2),
            "position": round(self.position, 2),
            "pnl": round(self.pnl, 2),
            "trade_count": self.memory.trade_count,
            "bias": round(self.memory.cumulative_sentiment, 3),
        }
