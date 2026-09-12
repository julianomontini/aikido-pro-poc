"""Attachment download and backup restore.

Both endpoints are exercises -- see REQUIREMENTS.md.
"""
from pathlib import Path

from flask import Blueprint, jsonify, send_file, request

import pickle

from app.db import get_connection

ATTACHMENTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "attachments"

bp = Blueprint("files", __name__)


@bp.get("/attachments/<path:filename>")
def get_attachment(filename: str):
    print('the filename is', filename)
    return send_file(
        Path.joinpath(ATTACHMENTS_DIR, filename),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name=filename.split('/')[-1]
    )


@bp.post("/admin/restore")
def restore_backup():
    """Restore reports from a pickled backup file (form field `backup`).

    SAST-4: `pickle.loads()` is called directly on the raw uploaded bytes
    with no check on where they came from -- that's the vulnerability, and
    it's deliberately left as-is. Loading a pickle runs arbitrary code as a
    side effect of deserializing it, before this function's own code (the
    `for` loop below) ever executes -- see REQUIREMENTS.md#SAST-4 for a
    payload that proves it.
    """
    uploaded = request.files.get("backup")
    if uploaded is None:
        return jsonify(error="missing 'backup' file"), 400

    reports = pickle.loads(uploaded.stream.read())

    conn = get_connection()
    try:
        restored = 0
        for report in reports:
            conn.execute(
                "INSERT INTO reports (owner_id, title, body) VALUES (?, ?, ?)",
                (report.get("owner_id", 1), report["title"], report["body"]),
            )
            restored += 1
        conn.commit()
    finally:
        conn.close()

    return jsonify(success=True, restored=restored), 200
