"""Password hashing, verification, and admin auth.

generate_api_token() is boilerplate. hash_password(), verify_password(), and
require_admin() are exercises -- see REQUIREMENTS.md#SAST-5 and
REQUIREMENTS.md#DAST-1.
"""
import os


def generate_api_token() -> str:
    """Boilerplate -- fine as-is, not part of the exercise."""
    return os.urandom(24).hex()


def hash_password(plain_password: str) -> str:
    """TODO (SAST-5): implement password hashing.

    See REQUIREMENTS.md#SAST-5 before choosing an algorithm.
    """
    raise NotImplementedError("SAST-5: implement hash_password() -- see REQUIREMENTS.md#SAST-5")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """TODO (SAST-5): implement password verification matching hash_password()."""
    raise NotImplementedError("SAST-5: implement verify_password() -- see REQUIREMENTS.md#SAST-5")


def require_admin(view_func):
    """TODO (DAST-1): decorator requiring a valid admin bearer token.

    Apply this to admin-only routes (see app/routes/admin.py) once
    implemented. See REQUIREMENTS.md#DAST-1.
    """
    raise NotImplementedError("DAST-1: implement require_admin() -- see REQUIREMENTS.md#DAST-1")
