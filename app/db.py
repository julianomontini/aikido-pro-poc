"""SQLite setup and seed data for the Reports Manager POC.

Boilerplate -- not part of any exercise. Safe to leave as-is.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "reports.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    api_token TEXT,
    is_admin INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
"""

SEED_REPORTS = [
    ("Q1 infra spend", "Cloud spend rose 12% quarter over quarter, mainly compute."),
    ("Incident postmortem - auth outage", "Root cause: expired certificate on the auth service."),
    ("Vendor security review - Acme SaaS", "No material findings. Renewal recommended."),
]


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        cur = conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                ("demo", "unset", 0),
            )
            conn.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                ("admin", "unset", 1),
            )
            for title, body in SEED_REPORTS:
                conn.execute(
                    "INSERT INTO reports (owner_id, title, body) VALUES (?, ?, ?)",
                    (1, title, body),
                )
        conn.commit()
    finally:
        conn.close()
