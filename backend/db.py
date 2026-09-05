"""
db.py — Persistence layer for learner progress records and decision history.

Uses SQLite so the hackathon demo has real persistence without needing a
server. Progress is stored as JSON blobs keyed by (learner_id, topic_id) —
fine at hackathon scale and easy to inspect/debug (open learning_coach.db
in any SQLite viewer).
"""

import sqlite3
import json
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "learning_coach.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            learner_id TEXT NOT NULL,
            topic_id TEXT NOT NULL,
            data TEXT NOT NULL,
            PRIMARY KEY (learner_id, topic_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decisions_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id TEXT NOT NULL,
            topic_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            reason_code TEXT NOT NULL,
            reasoning TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_progress(learner_id: str, topic_id: str) -> dict:
    """Fetch existing progress record, or return a fresh blank one."""
    conn = get_connection()
    row = conn.execute(
        "SELECT data FROM progress WHERE learner_id = ? AND topic_id = ?",
        (learner_id, topic_id),
    ).fetchone()
    conn.close()

    if row:
        return json.loads(row["data"])

    return {
        "learner_id": learner_id,
        "topic_id": topic_id,
        "attempts": [],
        "reinforcement_count": 0,
        "mastery_status": "not_started",
        "last_decision": None,
        "last_updated": None,
    }


def save_progress(progress: dict):
    progress["last_updated"] = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO progress (learner_id, topic_id, data)
        VALUES (?, ?, ?)
        ON CONFLICT(learner_id, topic_id)
        DO UPDATE SET data = excluded.data
        """,
        (progress["learner_id"], progress["topic_id"], json.dumps(progress)),
    )
    conn.commit()
    conn.close()


def get_all_progress_for_learner(learner_id: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT data FROM progress WHERE learner_id = ?", (learner_id,)
    ).fetchall()
    conn.close()
    return [json.loads(r["data"]) for r in rows]


def log_decision(learner_id: str, topic_id: str, decision: str, reason_code: str, reasoning: str):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO decisions_log (learner_id, topic_id, decision, reason_code, reasoning, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (learner_id, topic_id, decision, reason_code, reasoning, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def get_decision_history(learner_id: str = None) -> list:
    conn = get_connection()
    if learner_id:
        rows = conn.execute(
            "SELECT * FROM decisions_log WHERE learner_id = ? ORDER BY id",
            (learner_id,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM decisions_log ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def reset_db():
    """Wipe all data — useful when re-running demos from a clean slate."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
