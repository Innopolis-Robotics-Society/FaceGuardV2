"""Unit tests for recognition loop construction (critical module)."""

from __future__ import annotations

from unittest.mock import MagicMock

from app.recognition import RecognitionLoop


def test_recognition_loop_constructs_with_valid_params():
    db = MagicMock()
    ml = MagicMock()
    servo = MagicMock()
    state = MagicMock()

    loop = RecognitionLoop(
        db=db,
        ml=ml,
        servo=servo,
        state=state,
        threshold=0.45,
        interval_ms=500,
    )
    assert loop.threshold == 0.45
    assert loop.interval_ms == 500
    assert loop.db is db
    assert loop.servo is servo
