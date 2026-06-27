"""Camera stream proxy: forwards MJPEG from the ML service to browsers.

The ML service owns the camera (US: hardware ownership). The backend
proxies its MJPEG stream to the browser so the admin UI can show the
live feed without giving clients direct access to the ML service.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..auth import require_admin
from ..ml_client import MLClient

router = APIRouter()


@router.get("/stream")
async def stream(
    _admin=Depends(require_admin),
    ml: MLClient = Depends(),
):
    """Proxy the ML service's MJPEG stream to the browser."""

    async def generate():
        async for chunk in ml.stream_mjpeg():
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
