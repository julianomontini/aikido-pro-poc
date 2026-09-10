"""Report listing, search, and export.

list_reports() is boilerplate and already implemented.
search_reports() and export_report() are exercises -- see REQUIREMENTS.md.
"""
from flask import Blueprint, jsonify

from app.db import get_connection

bp = Blueprint("reports", __name__)


@bp.get("/reports")
def list_reports():
    """Boilerplate -- implemented. Not part of the exercise."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, title, created_at FROM reports ORDER BY created_at DESC"
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


@bp.get("/reports/search")
def search_reports():
    """TODO (SAST-1): search reports by title/body using the `q` query param.

    Render results via app/templates/search_results.html (that template has
    its own TODO -- see REQUIREMENTS.md#DAST-4).

    See REQUIREMENTS.md#SAST-1 before writing the query.
    """
    return jsonify(error="not implemented", requirement="SAST-1"), 501


@bp.get("/reports/<int:report_id>/export")
def export_report(report_id: int):
    """TODO (SAST-2): export a report to the format given by the `fmt`
    query param (e.g. txt, pdf, md) by shelling out to a converter.

    See REQUIREMENTS.md#SAST-2 before building the command.
    """
    return jsonify(error="not implemented", requirement="SAST-2"), 501
