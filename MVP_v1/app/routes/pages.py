"""Page routes: dashboard, registration form, logs.

User list + detail pages live in `routes/users.py` (issue #76/#77).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.templating import Jinja2Templates

from ..auth import require_admin
from ..database import FaceDatabase
from ..state import state

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def dashboard(
    request: Request,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    counts = db.counts()
    snapshot = state.snapshot()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "counts": counts,
            "snapshot": snapshot,
        },
    )


@router.get("/register")
async def register_page(
    request: Request,
    _admin=Depends(require_admin),
):
    return templates.TemplateResponse(
        request,
        "register.html",
        {
            "frame_count": 5,
        },
    )


@router.get("/register/options/{kind}")
async def register_options(
    kind: str,
    request: Request,
    _admin=Depends(require_admin),
):
    if kind == "temporary":
        return templates.TemplateResponse(
            request,
            "partials/guest_options.html",
            {},
        )
    return templates.TemplateResponse(
        request,
        "partials/guest_options.html",
        {},
    )


@router.get("/logs")
async def logs_page(
    request: Request,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
    today: bool = Query(False),
    q: str | None = Query(None),
):
    entries = db.list_logs(limit=300, today_only=today, user_filter=q)
    return templates.TemplateResponse(
        request,
        "logs.html",
        {
            "entries": entries,
            "today_filter": today,
            "query": q or "",
        },
    )


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}
