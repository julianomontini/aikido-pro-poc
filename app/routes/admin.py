"""Admin-only stats.

DAST-1: this endpoint originally shipped with no auth check at all --
that omission was the vulnerability. It's now behind app.auth.require_admin()
as the fix. See REQUIREMENTS.md#DAST-1.
"""
from flask import Blueprint, jsonify

from app.auth import require_admin
from app.db import get_connection

bp = Blueprint("admin", __name__)


@bp.get("/admin/stats")
@require_admin
def stats():
    conn = get_connection()
    try:
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        reports = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
        return jsonify(users=users, reports=reports)
    finally:
        conn.close()
