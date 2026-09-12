"""Report listing, search, and export.

list_reports() is boilerplate and already implemented.
search_reports() and export_report() are exercises -- see REQUIREMENTS.md.
"""
from flask import Blueprint, jsonify, request, render_template

from app.db import get_connection

import subprocess

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
    conn = get_connection()
    term = request.args.get('q', '')

    condition = f"title LIKE '%{term}%' OR body LIKE '%{term}%'" if len(term) else "1 = 1"
    query = f"SELECT title FROM reports WHERE {condition} ORDER BY created_at DESC"
    try:
        return render_template(
            'search_results.html', 
            reports=conn.execute(query).fetchall()
        )
    finally:
        conn.close()


@bp.get("/reports/<int:report_id>/export")
def export_report(report_id: int):
    fmt = request.args.get('fmt')
    subprocess.run(
        f"pandoc report_{report_id}.txt -o report_{report_id}.{fmt}",
        shell=True
    )
    return jsonify({'success': True})
