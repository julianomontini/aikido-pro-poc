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

# A bigger, more realistic set of reports -- plenty to search/export/list
# against once SAST-1/SAST-2 are implemented, without having to type
# anything in by hand. Not security-relevant itself; feel free to add more.
SEED_REPORTS = [
    ("Q1 infra spend", "Cloud spend rose 12% quarter over quarter, mainly compute."),
    ("Q2 infra spend", "Cloud spend down 4% after rightsizing the staging cluster."),
    ("Incident postmortem - auth outage", "Root cause: expired certificate on the auth service."),
    ("Incident postmortem - payment webhook retries", "Duplicate charges root-caused to a missing idempotency key on retry."),
    ("Incident postmortem - CI outage", "GitHub Actions runner queue backed up for 40 minutes during a provider incident."),
    ("Vendor security review - Acme SaaS", "No material findings. Renewal recommended."),
    ("Vendor security review - DataSync Inc", "SOC 2 Type II report on file. No material findings."),
    ("Access review - Q3", "Admin group membership audited; two stale accounts removed."),
    ("Pen test summary - external network", "No critical findings. Three medium findings tracked under SEC-482."),
    ("On-call handoff notes - week 37", "One paging incident, resolved in 12 minutes. No follow-up required."),
    ("Runbook - database failover", "Updated after last quarter's near-miss during a primary failover drill."),
    ("Compliance - GDPR data retention audit", "Logs retained 90 days as required. Audit confirmed compliant."),
]


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_seed_users(conn: sqlite3.Connection) -> int:
    """Create the demo/admin users if they don't exist yet.

    Returns the id of the "demo" user, used as the owner of seed reports.
    """
    row = conn.execute("SELECT id FROM users WHERE username = ?", ("demo",)).fetchone()
    if row is not None:
        return row["id"]

    conn.execute(
        "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
        ("demo", "unset", 0),
    )
    conn.execute(
        "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
        ("admin", "unset", 1),
    )
    return conn.execute("SELECT id FROM users WHERE username = ?", ("demo",)).fetchone()["id"]


def seed_reports(conn: sqlite3.Connection, owner_id: int) -> int:
    """Insert any SEED_REPORTS not already present (matched by title).

    Idempotent -- safe to call repeatedly (e.g. from scripts/seed.py)
    without creating duplicates. Returns how many rows were inserted.
    """
    existing_titles = {
        row["title"] for row in conn.execute("SELECT title FROM reports")
    }
    inserted = 0
    for title, body in SEED_REPORTS:
        if title in existing_titles:
            continue
        conn.execute(
            "INSERT INTO reports (owner_id, title, body) VALUES (?, ?, ?)",
            (owner_id, title, body),
        )
        inserted += 1
    return inserted


def init_db() -> None:
    """Boilerplate app-startup hook: create tables and seed once, quietly.

    For adding more seed data later, or resetting it, use scripts/seed.py
    instead of relying on this -- it only seeds when the DB is empty.
    """
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0] == 0:
            owner_id = ensure_seed_users(conn)
            seed_reports(conn, owner_id)
        conn.commit()
    finally:
        conn.close()
