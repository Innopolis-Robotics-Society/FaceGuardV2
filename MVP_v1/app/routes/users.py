"""CRUD routes for permanent users and temporary guests (US-02, US-03).

All routes are HTMX-driven. HTML fragments are returned for in-place
DOM swaps so the page never does a full reload.
"""

from __future__ import annotations

import asyncio
import logging

import numpy as np
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..auth import require_admin
from ..config import Settings, get_settings
from ..database import FaceDatabase
from ..ml_client import MLClient
from ..recognition import register_one

log = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/users/{user_id}/delete")
async def delete_user(
    user_id: int,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    if not db.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return RedirectResponse("/users", status_code=303)


@router.post("/guests/{guest_id}/delete")
async def delete_guest(
    guest_id: int,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    if not db.delete_guest(guest_id):
        raise HTTPException(status_code=404, detail="Guest not found")
    return RedirectResponse("/users", status_code=303)


@router.post("/guests/purge")
async def purge_guests(_admin=Depends(require_admin), db: FaceDatabase = Depends()):
    n = db.purge_expired_guests()
    return {"purged": n}


@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    access_type: str = Form(...),
    guest_days: int | None = Form(None),
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
    ml: MLClient = Depends(),
    settings: Settings = Depends(get_settings),
):
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    is_guest = access_type == "temporary"
    if is_guest and (not guest_days or guest_days <= 0):
        raise HTTPException(
            status_code=400,
            detail="Temporary access requires a positive number of days",
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
            guest_days=guest_days,
            frame_count=settings.registration_frame_count,
            frame_interval_ms=settings.registration_frame_interval_ms,
        )
    except RuntimeError as e:
        log.warning("Registration failed: %s", e)
        return templates.TemplateResponse(
            request,
            "partials/register_result.html",
            {
                "ok": False,
                "message": str(e),
            },
            status_code=502,
        )
    except Exception as e:
        log.exception("Unexpected registration error")
        return templates.TemplateResponse(
            request,
            "partials/register_result.html",
            {
                "ok": False,
                "message": f"Unexpected error: {e}",
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        request,
        "partials/register_result.html",
        {
            "ok": True,
            "message": msg,
            "preview": preview,
        },
    )


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
