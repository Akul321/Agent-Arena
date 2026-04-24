from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..agents.factory import ROLE_REGISTRY, build
from ..simulation.engine import arena


router = APIRouter(prefix="/api/agents", tags=["agents"])


class NewAgent(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    role: str
    strategy: str | None = None
    risk: float = Field(default=0.5, ge=0.05, le=1.0)


@router.get("")
def list_agents() -> dict:
    return {
        "agents": arena.list_agents(),
        "roles": list(ROLE_REGISTRY.keys()),
    }


@router.post("")
def add_agent(payload: NewAgent) -> dict:
    try:
        agent = build(
            payload.role, payload.name,
            strategy=payload.strategy, risk=payload.risk,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return arena.add_agent(agent)


@router.delete("/{agent_id}")
def remove_agent(agent_id: str) -> dict:
    if not arena.remove_agent(agent_id):
        raise HTTPException(status_code=404, detail="agent not found")
    return {"ok": True}
