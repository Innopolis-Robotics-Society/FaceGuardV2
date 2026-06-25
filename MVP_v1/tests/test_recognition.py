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
    assert loop._threshold == 0.45
    assert loop._interval == 0.5
    assert loop._db is db
    assert loop._servo is servo
