"""
Session-based isolation.

Each browser generates a UUID (stored client-side in Local Storage) which is
sent on every request via the X-Session-Id header. Every document write and
every vector-store query is scoped to this session_id, so one user's
documents are structurally unreachable from another session.

This is intentionally a lightweight stand-in for full authentication -- see
docs/Security.md for the production hardening path (JWT auth + RBAC).
"""
import uuid

from fastapi import Header, HTTPException


def get_session_id(x_session_id: str = Header(..., alias="X-Session-Id")) -> str:
    """FastAPI dependency: extracts and validates the session id header."""
    if not x_session_id:
        raise HTTPException(status_code=401, detail="Missing X-Session-Id header.")
    try:
        # Validate it is a well-formed UUID to prevent header abuse/injection.
        uuid.UUID(x_session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="X-Session-Id must be a valid UUID.")
    return x_session_id
