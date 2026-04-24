from __future__ import annotations

from .base import Agent
from .central_bank import CentralBank
from .hedge_fund import HedgeFund
from .quant import QuantAgent
from .retail_trader import RetailTrader


ROLE_REGISTRY: dict[str, type[Agent]] = {
    "Retail Trader": RetailTrader,
    "Hedge Fund": HedgeFund,
    "Quant": QuantAgent,
    "Central Bank": CentralBank,
}


def build(role: str, name: str, *, strategy: str | None = None,
          risk: float = 0.5) -> Agent:
    cls = ROLE_REGISTRY.get(role)
    if not cls:
        raise ValueError(
            f"Unknown role '{role}'. Options: {list(ROLE_REGISTRY)}"
        )
    return cls(name=name, strategy=strategy, risk=risk)


def default_roster() -> list[Agent]:
    return [
        RetailTrader("Apex Retail", risk=0.6),
        RetailTrader("Reddit Rally", strategy="momentum", risk=0.8),
        HedgeFund("Meridian Capital", risk=0.7),
        HedgeFund("Polaris Macro", strategy="risk_off", risk=0.5),
        QuantAgent("Sigma Quant", risk=0.55),
        CentralBank("Federal Reserve", risk=1.0),
    ]
