# db/database.py — SQLite connection + CRUD helpers
import sqlite3
import os
import json
import uuid

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH, SCHEMA_PATH


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row-factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create all tables from schema.sql if they don't exist."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


# ─── Case CRUD ────────────────────────────────────────────────────────

def insert_case(
    title: str,
    description: str,
    category: str,
    jurisdiction: str,
    claim_amount: float,
    plaintiff_name: str,
    defendant_name: str,
) -> str:
    """Insert a new case and its entities/edges. Returns the case ID."""
    conn = get_connection()
    case_id = str(uuid.uuid4())[:8]
    plaintiff_id = str(uuid.uuid4())[:8]
    defendant_id = str(uuid.uuid4())[:8]

    # Insert entities
    conn.execute(
        "INSERT OR IGNORE INTO entities (id, name, type) VALUES (?, ?, ?)",
        (plaintiff_id, plaintiff_name, "person"),
    )
    conn.execute(
        "INSERT OR IGNORE INTO entities (id, name, type) VALUES (?, ?, ?)",
        (defendant_id, defendant_name, "person"),
    )

    # Insert case
    conn.execute(
        """INSERT INTO cases (id, title, description, category, jurisdiction,
           claim_amount, plaintiff_id, defendant_id, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'intake')""",
        (case_id, title, description, category, jurisdiction,
         claim_amount, plaintiff_id, defendant_id),
    )

    # Insert edges
    conn.execute(
        "INSERT INTO case_edges (case_id, entity_a, entity_b, edge_type) VALUES (?, ?, ?, ?)",
        (case_id, plaintiff_id, defendant_id, "plaintiff_vs_defendant"),
    )

    conn.commit()
    conn.close()
    return case_id


def update_case(case_id: str, **kwargs):
    """Update one or more fields on a case row."""
    conn = get_connection()
    set_clause = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [case_id]
    conn.execute(f"UPDATE cases SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def get_case(case_id: str) -> dict | None:
    """Fetch a single case by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_cases() -> list[dict]:
    """Fetch all cases ordered by filed_at desc."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM cases ORDER BY filed_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_cases_by_status(status: str) -> list[dict]:
    """Fetch cases filtered by status."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM cases WHERE status = ? ORDER BY filed_at DESC", (status,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Entity helpers ───────────────────────────────────────────────────

def insert_entity(entity_id: str, name: str, entity_type: str):
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO entities (id, name, type) VALUES (?, ?, ?)",
        (entity_id, name, entity_type),
    )
    conn.commit()
    conn.close()


def get_entity(entity_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM entities WHERE id = ?", (entity_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_entity_name(entity_id: str) -> str:
    """Return the name of an entity, or the ID if not found."""
    entity = get_entity(entity_id)
    return entity["name"] if entity else entity_id


# ─── Edge helpers ─────────────────────────────────────────────────────

def insert_edge(case_id: str, entity_a: str, entity_b: str, edge_type: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO case_edges (case_id, entity_a, entity_b, edge_type) VALUES (?, ?, ?, ?)",
        (case_id, entity_a, entity_b, edge_type),
    )
    conn.commit()
    conn.close()


# ─── Negotiation log ─────────────────────────────────────────────────

def insert_negotiation_turn(case_id: str, turn: int, speaker: str, message: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO negotiation_log (case_id, turn, speaker, message) VALUES (?, ?, ?, ?)",
        (case_id, turn, speaker, message),
    )
    conn.commit()
    conn.close()


def get_negotiation_log(case_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM negotiation_log WHERE case_id = ? ORDER BY turn",
        (case_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Duplicate check ─────────────────────────────────────────────────

def check_duplicate(plaintiff_id: str, defendant_id: str, category: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        """SELECT * FROM cases
           WHERE plaintiff_id = ? AND defendant_id = ? AND category = ?
           AND status NOT IN ('resolved', 'dismissed')
           LIMIT 1""",
        (plaintiff_id, defendant_id, category),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Historical cases ────────────────────────────────────────────────

def get_historical_cases() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM historical_cases").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_historical_case(
    case_id: str, summary: str, category: str, outcome: str,
    dna_vector: list[float], jurisdiction: str, year: int
):
    conn = get_connection()
    conn.execute(
        """INSERT OR IGNORE INTO historical_cases
           (id, summary, category, outcome, dna_vector, jurisdiction, year)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (case_id, summary, category, outcome, json.dumps(dna_vector), jurisdiction, year),
    )
    conn.commit()
    conn.close()
