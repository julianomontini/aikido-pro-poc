"""Reseed the reports database with the sample dataset in app/db.py.

Boilerplate -- not part of any SAST/SCA/DAST exercise. Run this whenever
you want the full sample set of reports available (e.g. after clearing the
DB, or because you started the app before this script existed and only
have the original 3 seed reports).

Usage:
    poetry run python scripts/seed.py            # add any missing seed reports
    poetry run python scripts/seed.py --reset     # delete the DB file, then reseed from scratch
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import DB_PATH, SCHEMA, ensure_seed_users, get_connection, seed_reports  # noqa: E402


def reset_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Deleted {DB_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="delete the DB file first, then reseed from scratch",
    )
    args = parser.parse_args()

    if args.reset:
        reset_db()

    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        owner_id = ensure_seed_users(conn)
        added = seed_reports(conn, owner_id)
        conn.commit()
        total = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    finally:
        conn.close()

    print(f"Added {added} new report(s); {total} total in {DB_PATH}")


if __name__ == "__main__":
    main()
