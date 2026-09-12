"""Password hashing, verification, and admin auth.

generate_api_token() is boilerplate. hash_password(), verify_password(), and
require_admin() are exercises -- see REQUIREMENTS.md#SAST-5 and
REQUIREMENTS.md#DAST-1.
"""
import hashlib
import os
from functools import wraps

from flask import jsonify, request

from app.db import get_connection


def generate_api_token() -> str:
    """Boilerplate -- fine as-is, not part of the exercise."""
    return os.urandom(24).hex()


def hash_password(plain_password: str) -> str:
    """SAST-5: weak/broken cryptography, deliberately.

    Unsalted MD5 -- no per-user salt, no work factor, trivially reversible
    via rainbow tables. See REQUIREMENTS.md#SAST-5.
    """
    return hashlib.md5(plain_password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, password_hash: str) -> bool:
    """SAST-5: matches hash_password()'s weak hash with a plain `==` compare

    (not constant-time, but that's a secondary concern next to using MD5
    unsalted in the first place).
    """
    return hash_password(plain_password) == password_hash


def require_admin(view_func):
    """DAST-1 fix: require a valid admin bearer token.

    Expects `Authorization: Bearer <token>` and checks it against the
    `api_token` stored for a user with `is_admin = 1`. Apply this to
    admin-only routes (see app/routes/admin.py). See REQUIREMENTS.md#DAST-1.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return jsonify(error="missing or malformed Authorization header"), 401

        conn = get_connection()
        try:
            admin = conn.execute(
                "SELECT id FROM users WHERE is_admin = 1 AND api_token = ?",
                (token,),
            ).fetchone()
        finally:
            conn.close()

        if admin is None:
            return jsonify(error="invalid admin token"), 403

        return view_func(*args, **kwargs)

    return wrapper
