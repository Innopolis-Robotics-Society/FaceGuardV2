"""Unit tests for recognition loop (critical module - core user workflow)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.recognition import RecognitionLoop


def test_recognition_loop_constructs_with_valid_params():
    db = MagicMock()
    ml = MagicMock()
    servo = MagicMock()
    state = MagicMock()
    leds = MagiMock()
    loop = RecognitionLoop(
        db=db,
        ml=ml,
        servo=servo,
        state=state,
        threshold=0.45,
        interval_ms=500,
        leds = leds,
    )
    assert loop._threshold == 0.45
    assert loop._interval == 0.5
    assert loop._db is db
    assert loop._servo is servo


@pytest.mark.asyncio
async def test_tick_ml_unhealthy_sets_error():
    """ML down → state error (no crash)."""
    state = MagicMock()
    ml = MagicMock()
    ml.health = AsyncMock(return_value=False)

    loop = RecognitionLoop(
        db=MagicMock(),
        ml=ml,
        servo=MagicMock(),
        state=state,
        threshold=0.5,
        interval_ms=1000,
        leds = MagiMock(),
    )
    await loop._tick()

    state.set_ml_health.assert_called_once_with(False)
    assert state.update.call_args[0][0].verdict == "error"


@pytest.mark.asyncio
async def test_tick_no_faces_sets_idle():
    """No faces in frame → idle state."""
    state = MagicMock()
    ml = MagicMock()
    ml.health = AsyncMock(return_value=True)

    frame = MagicMock()
    frame.faces = []
    ml.get_latest = AsyncMock(return_value=frame)

    loop = RecognitionLoop(
        db=MagicMock(),
        ml=ml,
        servo=MagicMock(),
        state=state,
        threshold=0.5,
        interval_ms=1000,
        leds = MagiMock(),
    )
    loop._last_health_check = 0
    await loop._tick()

    assert state.update.call_args[0][0].verdict == "idle"


@pytest.mark.asyncio
async def test_tick_granted_triggers_servo():
    """Known face → granted + servo open."""
    state = MagicMock()
    ml = MagicMock()
    servo = MagicMock()
    ml.health = AsyncMock(return_value=True)
    leds = MagiMock(),
    face = MagicMock()
    face.bbox = [0, 0, 100, 100]
    face.embedding = [0.5] * 512

    frame = MagicMock()
    frame.faces = [face]
    ml.get_latest = AsyncMock(return_value=frame)

    db = MagicMock()
    result = MagicMock()
    result.access_type = "user"
    result.name = "Alice"
    result.score = 0.85
    result.matched_user_id = 1
    db.recognize.return_value = result

    loop = RecognitionLoop(
        db=db,
        ml=ml,
        servo=servo,
        state=state,
        threshold=0.5,
        interval_ms=1000,
        leds = leds,
    )
    loop._last_health_check = 0

    with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
        mock_thread.side_effect = [result, None, None]
        await loop._tick()

    assert state.update.call_args[0][0].verdict == "granted"
    assert state.update.call_args[0][0].name == "Alice"
    assert mock_thread.call_count == 3
