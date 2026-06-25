"""Page routes: dashboard, users list, registration form, logs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
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
        "dashboard.html",
        {
            "request": request,
            "counts": counts,
            "snapshot": snapshot,
        },
    )


@router.get("/users")
async def users_page(
    request: Request,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
):
    users = db.list_users()
    guests = db.list_guests(include_expired=False)
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "users": users,
            "guests": guests,
        },
    )


@router.get("/register")
async def register_page(
    request: Request,
    _admin=Depends(require_admin),
):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "frame_count": 5,  # default; overridden by settings in real flow
        },
    )


@router.get("/logs")
async def logs_page(
    request: Request,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
    today: bool = False,
    q: str | None = None,
):
    entries = db.list_logs(limit=300, today_only=today, user_filter=q)
    return templates.TemplateResponse(
        "logs.html",
        {
            "request": request,
            "entries": entries,
            "today_filter": today,
            "query": q or "",
        },
    )


@router.get("/register/options/{kind}")
async def register_options(
    kind: str,
    request: Request,
    _admin=Depends(require_admin),
):
    """Return the partial form fragment for the selected access type."""
    if kind == "temporary":
        return templates.TemplateResponse(
            "partials/guest_options.html",
            {"request": request},
        )
    # Permanent — no extra fields needed.
    return templates.TemplateResponse(
        "partials/guest_options.html",
        {"request": request},
    )


@router.get("/healthz")
async def healthz():
    """Unauthenticated health probe (for Docker / load balancer)."""
    return {"status": "ok"}
