"""Attachment download and backup restore.

Both endpoints are exercises -- see REQUIREMENTS.md.
"""
from pathlib import Path

from flask import Blueprint, jsonify

ATTACHMENTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "attachments"

bp = Blueprint("files", __name__)


@bp.get("/attachments/<path:filename>")
def get_attachment(filename: str):
    """TODO (SAST-3): serve `filename` from ATTACHMENTS_DIR.

    See REQUIREMENTS.md#SAST-3 before joining the path.
    """
    return jsonify(error="not implemented", requirement="SAST-3"), 501


@bp.post("/admin/restore")
def restore_backup():
    """TODO (SAST-4): accept an uploaded backup file (form field `backup`)
    describing reports to restore, and load it.

    See REQUIREMENTS.md#SAST-4 before picking how to parse it.
    """
    return jsonify(error="not implemented", requirement="SAST-4"), 501
