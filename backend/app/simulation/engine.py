"""Simulation engine — coordinates agents, market, and history."""
from __future__ import annotations

import datetime as dt
import threading

from ..agents.base import Agent, Decision, Event, MarketSnapshot
from ..agents.factory import default_roster
from ..db import get_conn, init_db
from .market import Market


def _narrative(event: Event, shock: float, decisions: list[Decision]) -> str:
    bulls = sum(1 for d in decisions if d.action == "buy")
    bears = sum(1 for d in decisions if d.action == "sell")
    direction = "rallied" if shock > 0 else "sold off" if shock < 0 else "stayed flat"
    bias = (
        "with buyers in control" if bulls > bears else
        "with sellers pressing" if bears > bulls else
        "as the tape split"
    )
    return (
        f"\"{event.headline}\" — market {direction} "
        f"{abs(shock) * 100:.2f}% {bias} ({bulls} bids, {bears} offers)."
    )


class Arena:
    def __init__(self) -> None:
        init_db()
        self.market = Market()
        self.agents: list[Agent] = default_roster()
        self._lock = threading.Lock()

    # ---- agent registry -------------------------------------------------
    def list_agents(self) -> list[dict]:
        with self._lock:
            for a in self.agents:
                a.mark(self.market.price)
            return [a.to_dict() for a in self.agents]

    def add_agent(self, agent: Agent) -> dict:
        with self._lock:
            self.agents.append(agent)
            agent.mark(self.market.price)
            return agent.to_dict()

    def remove_agent(self, agent_id: str) -> bool:
        with self._lock:
            before = len(self.agents)
            self.agents = [a for a in self.agents if a.id != agent_id]
            return len(self.agents) < before

    # ---- simulation step ------------------------------------------------
    def run_event(self, event: Event) -> dict:
        with self._lock:
            price_before = self.market.price

            # Step 1: instantaneous reaction to the event.
            shock = self.market.apply_shock(event.sentiment, event.magnitude)

            snapshot = MarketSnapshot(
                price=self.market.price,
                trend=self.market.trend(),
                volatility=self.market.volatility(),
                sentiment=self.market.sentiment,
            )

            # Step 2: agents react.
            decisions: list[Decision] = []
            net_flow = 0.0
            for agent in self.agents:
                decision = agent.decide(snapshot, event)
                decisions.append(decision)
                if decision.action == "buy":
                    net_flow += decision.size
                elif decision.action == "sell":
                    net_flow -= decision.size

            # Step 3: settle against the market maker.
            impact = self.market.apply_flow(net_flow)
            for agent, decision in zip(self.agents, decisions):
                if decision.action != "hold" and decision.size > 0:
                    agent.settle(decision.action, decision.size, self.market.price)
                agent.mark(self.market.price)

            # Step 4: record tape + history.
            self.market.record(event=event.headline)
            narrative = _narrative(event, shock + impact, decisions)
            sim_id = self._persist(
                event=event,
                price_before=price_before,
                price_after=self.market.price,
                narrative=narrative,
                decisions=decisions,
            )

            return {
                "simulation_id": sim_id,
                "event": {
                    "headline": event.headline,
                    "summary": event.summary,
                    "source": event.source,
                    "sentiment": round(event.sentiment, 3),
                    "magnitude": round(event.magnitude, 3),
                },
                "market": self.market.snapshot_dict(),
                "price_before": round(price_before, 4),
                "price_after": round(self.market.price, 4),
                "shock_pct": round((shock + impact) * 100, 3),
                "decisions": [
                    {
                        "agent_id": d.agent_id,
                        "agent_name": d.agent_name,
                        "agent_role": d.agent_role,
                        "action": d.action,
                        "size": round(d.size, 2),
                        "rationale": d.rationale,
                    } for d in decisions
                ],
                "narrative": narrative,
                "agents": [a.to_dict() for a in self.agents],
            }

    # ---- state --------------------------------------------------------
    def state(self) -> dict:
        with self._lock:
            for a in self.agents:
                a.mark(self.market.price)
            return {
                "market": self.market.snapshot_dict(),
                "agents": [a.to_dict() for a in self.agents],
            }

    def reset(self) -> None:
        with self._lock:
            self.market = Market()
            self.agents = default_roster()

    # ---- persistence --------------------------------------------------
    def _persist(
        self, *, event: Event, price_before: float, price_after: float,
        narrative: str, decisions: list[Decision],
    ) -> int:
        now = dt.datetime.utcnow().isoformat() + "Z"
        with get_conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO simulations
                    (created_at, headline, source, sentiment,
                     price_before, price_after, narrative)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (now, event.headline, event.source, event.sentiment,
                 price_before, price_after, narrative),
            )
            sim_id = int(cur.lastrowid)
            conn.executemany(
                """
                INSERT INTO simulation_decisions
                    (simulation_id, agent_id, agent_name, agent_role,
                     action, size, rationale)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (sim_id, d.agent_id, d.agent_name, d.agent_role,
                     d.action, d.size, d.rationale)
                    for d in decisions
                ],
            )
        return sim_id

    def history(self, limit: int = 25) -> list[dict]:
        with get_conn() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, headline, source, sentiment,
                       price_before, price_after, narrative
                FROM simulations
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            out: list[dict] = []
            for r in rows:
                decisions = conn.execute(
                    """
                    SELECT agent_id, agent_name, agent_role,
                           action, size, rationale
                    FROM simulation_decisions
                    WHERE simulation_id = ?
                    """,
                    (r["id"],),
                ).fetchall()
                out.append({
                    "id": r["id"],
                    "created_at": r["created_at"],
                    "headline": r["headline"],
                    "source": r["source"],
                    "sentiment": r["sentiment"],
                    "price_before": r["price_before"],
                    "price_after": r["price_after"],
                    "narrative": r["narrative"],
                    "decisions": [dict(d) for d in decisions],
                })
            return out


arena = Arena()
