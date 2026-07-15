"""CRUD routes for users.

Endpoints:
  HTML (admin UI):
    GET  /users                     — list page
    GET  /users/{id}                — detail + edit page
    POST /users/{id}/delete         — delete (form submit)
    POST /users/{id}/update         — update fields (form submit)
    POST /register                  — 5-frame registration
    GET  /register/options/{kind}   — HTMX partial (see routes/pages.py)

  JSON API:
    GET    /backend/users           — list (optional ?type= filter)
    GET    /backend/users/{id}      — fetch one user
    PUT    /backend/users/{id}      — update one user
    DELETE /backend/users/{id}      — delete one user

All routes require an admin session.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import numpy as np
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse

from ..auth import require_admin
from ..config import Settings, get_settings
from ..database import FaceDatabase, User
from ..jinja import templates
from ..ml_client import MLClient
from ..recognition import register_one

log = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _user_to_dict(u: User) -> dict:
    """JSON-serializable view of a user (no embedding — too big)."""
    return {
        "id": u.id,
        "name": u.name,
        "type": u.type,
        "expires_at": u.expires_at.isoformat() if u.expires_at else None,
        "created_at": u.created_at.isoformat(),
    }


def _parse_iso_or_400(s: str | None, field: str) -> datetime | None:
    """Parse an ISO 8601 string into a UTC-aware datetime.

    Naive strings (e.g. from ``<input type="datetime-local">``, which
    drops timezone info) are interpreted as local time according to
    ``settings.local_timezone`` and converted to UTC.
    """
    if s is None or s == "":
        return None
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid {field}: {s!r}") from e
    if dt.tzinfo is None:
        # Naive datetime from a datetime-local input — treat as local.
        tz = ZoneInfo(get_settings().local_timezone)
        dt = dt.replace(tzinfo=tz)
    return dt.astimezone(UTC)


# ---------------------------------------------------------------------------
# HTML: list + detail + edit
# ---------------------------------------------------------------------------


@router.get("/users")
async def users_page(
    request: Request,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    users = db.list_users(type_filter="permanent")
    guests = db.list_users(type_filter="temporary", include_expired=False)
    return templates.TemplateResponse(
        request,
        "users.html",
        {
            "users": users,
            "guests": guests,
        },
    )


@router.get("/users/{user_id}")
async def user_detail_page(
    request: Request,
    user_id: int,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    """User detail + edit page with recent activity log."""
    user = db.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    logs = db.list_logs(limit=50, user_filter=user.name)
    return templates.TemplateResponse(
        request,
        "user_detail.html",
        {
            "user": user,
            "logs": logs,
        },
    )


@router.post("/users/{user_id}/update")
async def user_update_form(
    request: Request,
    user_id: int,
    name: str = Form(...),
    type: str = Form(...),
    expires_at: str = Form(None),
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    """Handle edit form submission. Forwards to db.update_user()."""
    user = db.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    if type not in ("permanent", "temporary"):
        raise HTTPException(status_code=400, detail="Invalid type")

    if type == "temporary":
        expires_dt = _parse_iso_or_400(expires_at, "expires_at")
        if expires_dt is None:
            raise HTTPException(
                status_code=400,
                detail="Temporary users require an expiration date",
            )
        if expires_dt <= datetime.now(UTC):
            raise HTTPException(
                status_code=400,
                detail="Expiration date must be in the future",
            )
    else:
        expires_dt = None  # permanent — clear

    try:
        updated = db.update_user(
            user_id,
            name=name,
            type=type,  # type: ignore[arg-type]
            expires_at=expires_dt,
        )
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    if updated is None:
        raise HTTPException(status_code=404, detail="User not found after update")

    return RedirectResponse(f"/users/{user_id}", status_code=303)


@router.post("/users/{user_id}/delete")
async def delete_user(
    user_id: int,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    if not db.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return RedirectResponse("/users", status_code=303)


# Legacy aliases kept for backward compatibility with old bookmarks/templates.
@router.post("/guests/{guest_id}/delete")
async def delete_guest_alias(
    guest_id: int,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    return await delete_user(guest_id, _admin, db)  # type: ignore[arg-type]


@router.post("/guests/purge")
async def purge_guests(_admin=Depends(require_admin), db: FaceDatabase = Depends()):
    n = db.purge_expired()
    return {"purged": n}


# ---------------------------------------------------------------------------
# Registration (US-02)
# ---------------------------------------------------------------------------


@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    access_type: str = Form(...),
    expires_at: str = Form(None),
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
    ml: MLClient = Depends(),
    settings: Settings = Depends(get_settings),
):
    """Capture 5 frames from the camera and register a new user.

    For ``access_type=temporary`` the form must include ``expires_at``
    (a naive local datetime from <input type="datetime-local">).
    """
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    is_guest = access_type == "temporary"
    expires_dt: datetime | None = None
    if is_guest:
        expires_dt = _parse_iso_or_400(expires_at, "expires_at")
        if expires_dt is None or expires_dt <= datetime.now(UTC):
            raise HTTPException(
                status_code=400,
                detail="Temporary access requires a future expiration date",
            )

    if not is_guest and db.get_user_by_name(name) is not None:
        return templates.TemplateResponse(
            request,
            "partials/register_result.html",
            {
                "ok": False,
                "message": f"User '{name}' already exists.",
            },
            status_code=409,
        )

    try:
        msg, preview = await asyncio.to_thread(
            register_one,
            db,
            ml,
            name=name,
            is_guest=is_guest,
            expires_at=expires_dt,
            frame_count=settings.registration_frame_count,
            frame_interval_ms=settings.registration_frame_interval_ms,
        )
    except RuntimeError as e:
        log.warning("Registration failed: %s", e)
        return templates.TemplateResponse(
            request,
            "partials/register_result.html",
            {"ok": False, "message": str(e)},
            status_code=502,
        )
    except Exception as e:
        log.exception("Unexpected registration error")
        return templates.TemplateResponse(
            request,
            "partials/register_result.html",
            {"ok": False, "message": f"Unexpected error: {e}"},
            status_code=500,
        )

    return templates.TemplateResponse(
        request,
        "partials/register_result.html",
        {"ok": True, "message": msg, "preview": preview},
    )


# ---------------------------------------------------------------------------
# JSON API — /backend/users[/{id}]
# ---------------------------------------------------------------------------


@router.get("/backend/users")
async def api_list_users(
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
    type: str | None = Query(None),
    include_expired: bool = Query(True),
):
    """List users as JSON. Optional ``?type=permanent|temporary`` and
    ``?include_expired=false`` filters."""
    type_filter = None  # type: ignore[assignment]
    if type in ("permanent", "temporary"):
        type_filter = type  # type: ignore[assignment]
    users = db.list_users(type_filter=type_filter, include_expired=include_expired)
    return {"users": [_user_to_dict(u) for u in users]}


@router.get("/backend/users/{user_id}")
async def api_get_user(
    user_id: int,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    """Fetch one user as JSON."""
    user = db.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_to_dict(user)


@router.put("/backend/users/{user_id}")
async def api_update_user(
    user_id: int,
    request: Request,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    """Update one user. Body is JSON with any of:
        {name, type, expires_at, embedding}

    ``type`` must be 'permanent' or 'temporary'.
    ``expires_at`` is an ISO 8601 string; required if type='temporary',
    ignored (and cleared) if type='permanent'.
    ``embedding`` is a list of 512 floats; if provided, replaces the
    stored embedding.
    """
    try:
        body = await request.json()
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid JSON body") from e
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Body must be a JSON object")

    name = body.get("name")
    if name is not None:
        if not isinstance(name, str) or not name.strip():
            raise HTTPException(status_code=400, detail="name must be a non-empty string")
        name = name.strip()

    new_type = body.get("type")
    if new_type is not None and new_type not in ("permanent", "temporary"):
        raise HTTPException(status_code=400, detail="type must be 'permanent' or 'temporary'")

    expires_raw = body.get("expires_at")
    expires_dt = _parse_iso_or_400(expires_raw, "expires_at") if expires_raw else None

    if new_type == "temporary" and expires_dt is None:
        # Check if the existing user already has expires_at set.
        existing = db.get_user(user_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="User not found")
        if existing.expires_at is None or existing.expires_at <= datetime.now(UTC):
            raise HTTPException(
                status_code=400,
                detail="temporary users require expires_at to be set",
            )

    embedding = None
    if "embedding" in body:
        emb_list = body["embedding"]
        if not isinstance(emb_list, list) or len(emb_list) != 512:
            raise HTTPException(status_code=400, detail="embedding must be a list of 512 floats")
        try:
            embedding = np.asarray(emb_list, dtype=np.float32)
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=400, detail="embedding must contain floats") from e

    try:
        updated = db.update_user(
            user_id,
            name=name,
            type=new_type,  # type: ignore[arg-type]
            expires_at=expires_dt,
            embedding=embedding,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        # sqlite3.IntegrityError (duplicate name) -> 409
        if "UNIQUE" in str(e).upper():
            raise HTTPException(status_code=409, detail=str(e)) from e
        raise HTTPException(status_code=500, detail=str(e)) from e

    if updated is None:
        raise HTTPException(status_code=404, detail="User not found")

    return _user_to_dict(updated)


@router.delete("/backend/users/{user_id}")
async def api_delete_user(
    user_id: int,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    if not db.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse({"deleted": user_id})


# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------


@router.post("/debug/seed-user")
async def debug_seed_user(
    name: str = Form(...),
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
    settings: Settings = Depends(get_settings),
):
    if not getattr(settings, "allow_debug_seed", False):
        raise HTTPException(status_code=404)
    rng = np.random.default_rng(abs(hash(name)) % (2**32))
    emb = rng.standard_normal(512).astype(np.float32)
    emb = emb / np.linalg.norm(emb)
    try:
        db.register_user(name, emb)
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return RedirectResponse("/users", status_code=303)
