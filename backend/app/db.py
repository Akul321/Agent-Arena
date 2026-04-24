import sqlite3
from contextlib import contextmanager
from typing import Iterator

from .config import DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS simulations (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at   TEXT NOT NULL,
    headline     TEXT NOT NULL,
    source       TEXT,
    sentiment    REAL,
    price_before REAL,
    price_after  REAL,
    narrative    TEXT
);

CREATE TABLE IF NOT EXISTS simulation_decisions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    simulation_id  INTEGER NOT NULL,
    agent_id       TEXT NOT NULL,
    agent_name     TEXT NOT NULL,
    agent_role     TEXT NOT NULL,
    action         TEXT NOT NULL,
    size           REAL NOT NULL,
    rationale      TEXT,
    FOREIGN KEY (simulation_id) REFERENCES simulations(id)
);

CREATE INDEX IF NOT EXISTS idx_decisions_sim
    ON simulation_decisions(simulation_id);
"""


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
