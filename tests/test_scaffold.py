"""Scaffold-integrity checks.

These assert that not-yet-implemented exercise endpoints still return 501.
As you implement each requirement, DELETE the matching test function -- a
failing test in this file after you've implemented something is expected
and correct, not a bug. If every test below is gone, SAST-1..4 are done.
"""
from app.main import app


def test_search_not_yet_implemented():
    """Delete once SAST-1 is implemented."""
    client = app.test_client()
    resp = client.get("/reports/search?q=test")
    assert resp.status_code == 501


def test_export_not_yet_implemented():
    """Delete once SAST-2 is implemented."""
    client = app.test_client()
    resp = client.get("/reports/1/export?fmt=txt")
    assert resp.status_code == 501


def test_attachment_not_yet_implemented():
    """Delete once SAST-3 is implemented."""
    client = app.test_client()
    resp = client.get("/attachments/example.txt")
    assert resp.status_code == 501


def test_restore_not_yet_implemented():
    """Delete once SAST-4 is implemented."""
    client = app.test_client()
    resp = client.post("/admin/restore")
    assert resp.status_code == 501
