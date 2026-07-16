"""Page routes: dashboard, registration form, logs.

User list + detail pages live in `routes/users.py`.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, Request

from ..auth import require_admin
from ..config import get_settings
from ..database import FaceDatabase
from ..jinja import templates
from ..state import state

router = APIRouter()


def _default_expires_local() -> str:
    """Return the default expiration (7 days from now) as a naive local
    datetime string suitable for <input type="datetime-local">."""
    s = get_settings()
    return (
        (datetime.now(UTC) + timedelta(days=7))
        .astimezone(ZoneInfo(s.local_timezone))
        .strftime("%Y-%m-%dT%H:%M")
    )


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
    s = get_settings()
    return templates.TemplateResponse(
        request,
        "register.html",
        {
            "frame_count": s.registration_frame_count,
            "default_expires": _default_expires_local(),
        },
    )


@router.get("/register/options/{kind}")
async def register_options(
    kind: str,
    request: Request,
    _admin=Depends(require_admin),
):
    """HTMX partial swap target for the access-type radio group.

    Returns the expiration-date picker when ``kind=temporary`` and an
    empty fragment when ``kind=permanent`` (so the picker is removed
    from the DOM when the user switches back).
    """
    if kind == "temporary":
        return templates.TemplateResponse(
            request,
            "partials/guest_options.html",
            {"default_expires": _default_expires_local()},
        )
    return templates.TemplateResponse(
        request,
        "partials/empty.html",
        {},
    )


@router.get("/logs")
async def logs_page(
    request: Request,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
    range: str = Query("all"),
    q: str | None = Query(None),
    today: bool = Query(False),  # legacy, kept for old bookmarks
):
    """Render the access-log page.

    ``range`` accepts 'today', 'week', or 'all'. The legacy ``today``
    boolean is still respected for backwards compatibility.
    """
    today_only = today or range == "today"
    week_only = range == "week"
    entries = db.list_logs(
        limit=300,
        today_only=today_only,
        week_only=week_only,
        user_filter=q,
    )
    return templates.TemplateResponse(
        request,
        "logs.html",
        {
            "entries": entries,
            "range": range if range in ("today", "week", "all") else "all",
            "query": q or "",
        },
    )


@router.get("/logs/table")
async def logs_table_partial(
    request: Request,
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
    range: str = Query("all"),
    q: str | None = Query(None),
):
    """HTMX partial — returns just the table HTML for live refresh.

    The logs page polls this endpoint every 5 seconds and swaps the
    table container without reloading the filters.
    """
    today_only = range == "today"
    week_only = range == "week"
    entries = db.list_logs(
        limit=300,
        today_only=today_only,
        week_only=week_only,
        user_filter=q,
    )
    return templates.TemplateResponse(
        request,
        "partials/logs_table.html",
        {
            "entries": entries,
        },
    )


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}
