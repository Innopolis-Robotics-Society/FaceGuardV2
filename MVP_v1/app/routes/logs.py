"""Logs API (US-10)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..auth import require_admin
from ..database import FaceDatabase

router = APIRouter()


@router.get("/api/logs")
async def list_logs(
    _admin=Depends(require_admin),
    db: FaceDatabase = Depends(),
    limit: int = Query(200, ge=1, le=1000),
    today: bool = Query(False),
    q: str | None = Query(None),
):
    entries = db.list_logs(limit=limit, today_only=today, user_filter=q)
    return {
        "entries": [
            {
                "id": e.id,
                "name": e.name,
                "score": e.score,
                "access_type": e.access_type,
                "success": e.success,
                "timestamp": e.timestamp.isoformat(),
                "liveness_passed": e.liveness_passed,
            }
            for e in entries
        ]
    }
