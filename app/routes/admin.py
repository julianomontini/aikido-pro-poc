"""Admin-only stats.

TODO (DAST-1): this endpoint has no auth check at all -- that omission is
the vulnerability, and it's intentional: there is nothing to "introduce"
here. Confirm it's reachable unauthenticated (via a DAST scan, or just
curl), then implement app.auth.require_admin() and apply it below as the
fix. See REQUIREMENTS.md#DAST-1.
"""
from flask import Blueprint, jsonify

from app.db import get_connection

bp = Blueprint("admin", __name__)


@bp.get("/admin/stats")
def stats():
    conn = get_connection()
    try:
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        reports = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
        return jsonify(users=users, reports=reports)
    finally:
        conn.close()
