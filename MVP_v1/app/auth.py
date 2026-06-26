"""Session-based authentication for the admin web UI.

Uses FastAPI's `Session` middleware (signed cookies via itsdangerous) +
bcrypt-hashed passwords. No JWT, no tokens — just a server-side session
cookie scoped to the FaceGuard app.

The first admin is bootstrapped from env on startup (see
`bootstrap_admin_from_env`). After that, the only way to add admins is
through the (future) admin-management UI or by editing the DB directly.
"""

from __future__ import annotations

import bcrypt
from fastapi import Depends, HTTPException, Request, status

from .database import Admin, FaceDatabase

# Cookie lifetime — 12h. Long enough for an admin shift, short enough to
# expire if the laptop is left open.
SESSION_MAX_AGE_SECONDS = 12 * 3600


def hash_password(plain: str) -> str:
    """Bcrypt-hash a plaintext password. Returns a utf-8 str ready to store."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time bcrypt verification."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def bootstrap_admin_from_env(db: FaceDatabase, settings) -> Admin:
    """Insert the env-configured admin if no admin with that username exists.

    Precedence: if `ADMIN_PASSWORD_HASH` is set, use it directly (allows
    shipping pre-hashed credentials in Docker). Otherwise hash
    `ADMIN_PASSWORD` on the fly.

    Safe to call on every startup — no-op once the admin already exists.
    """
    username = settings.admin_username
    if settings.admin_password_is_hashed():
        password_hash = settings.admin_password_hash  # type: ignore[assignment]
    else:
        password_hash = hash_password(settings.admin_password_plain)
    return db.bootstrap_admin(username, password_hash)


def login(db: FaceDatabase, username: str, password: str) -> Admin:
    """Verify credentials and return the admin on success.

    Raises `HTTPException(401)` on bad credentials.
    """
    admin = db.get_admin_by_username(username)
    if admin is None or not verify_password(password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return admin


def require_admin(request: Request, db: FaceDatabase = Depends()) -> Admin:
    """FastAPI dependency: read admin id from session, return the Admin.

    Raises 401 if not authenticated, 404 if the admin was deleted since
    the session was issued.
    """
    admin_id = request.session.get("admin_id")
    if admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"Location": "/login"},
        )
    admin = db.get_admin(int(admin_id))
    if admin is None:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin account no longer exists",
        )
    return admin


def start_session(request: Request, admin: Admin) -> None:
    """Mark the admin as logged-in on the current session."""
    request.session["admin_id"] = admin.id
    request.session["username"] = admin.username


def end_session(request: Request) -> None:
    """Log out — clear the session."""
    request.session.clear()
