"""Shared Jinja2 templates instance with project-wide custom filters."""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from fastapi.templating import Jinja2Templates

from .config import get_settings

templates = Jinja2Templates(directory="app/templates")


def _localdt(value, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Render a (possibly UTC) datetime in the configured local timezone.

    Used in templates as ``{{ user.created_at|localdt }}`` or with a
    custom format: ``{{ user.expires_at|localdt('%Y-%m-%dT%H:%M') }}``.
    Naive datetimes are assumed to be UTC.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    tz = ZoneInfo(get_settings().local_timezone)
    return value.astimezone(tz).strftime(fmt)


templates.env.filters["localdt"] = _localdt
