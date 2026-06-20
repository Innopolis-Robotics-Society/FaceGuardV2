"""Live status via SSE (Server-Sent Events).

The browser subscribes to `/status/events` and receives a `verdict`
event every time the recognition loop updates the system state. Used by
the dashboard to render the live status bar without polling.
"""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from ..auth import require_admin
from ..state import state

router = APIRouter()


@router.get("/status/events")
async def status_events(
    request: Request,
    _admin=Depends(require_admin),
):
    queue = await state.subscribe()

    async def event_generator():
        try:
            # Send an initial snapshot so the UI is correct on connect.
            yield {"event": "verdict", "data": json.dumps(state.snapshot())}

            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {"event": "verdict", "data": json.dumps(payload)}
                except asyncio.TimeoutError:
                    # Heartbeat keeps the connection alive through proxies.
                    yield {"event": "ping", "data": "{}"}
        finally:
            state.unsubscribe(queue)

    return EventSourceResponse(event_generator())


@router.get("/status/snapshot")
async def status_snapshot(_admin=Depends(require_admin)):
    """One-shot status read — useful for initial page load."""
    return state.snapshot()
