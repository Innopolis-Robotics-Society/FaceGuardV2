"""Unit tests for SystemState (app/state.py).

Covers: snapshot structure, update propagation, subscriber fan-out,
set_ml_health, thread-safety basics.
"""

from __future__ import annotations

import asyncio
import time

import pytest

from app.state import CurrentVerdict, SystemState

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def state() -> SystemState:
    return SystemState()


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


def test_initial_snapshot_verdict_is_idle(state: SystemState):
    snap = state.snapshot()
    assert snap["verdict"] == "idle"


def test_initial_snapshot_has_required_keys(state: SystemState):
    snap = state.snapshot()
    required = {
        "verdict",
        "name",
        "score",
        "access_type",
        "matched_user_id",
        "timestamp",
        "is_door_open",
        "ml_healthy",
        "last_ml_check",
    }
    assert required.issubset(snap.keys())


def test_initial_ml_healthy_is_false(state: SystemState):
    assert state.snapshot()["ml_healthy"] is False


def test_initial_door_not_open(state: SystemState):
    assert state.snapshot()["is_door_open"] is False


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------


def test_update_changes_verdict(state: SystemState):
    v = CurrentVerdict(
        verdict="granted", name="Alice", score=0.92, access_type="user", matched_user_id=1
    )
    state.update(v)
    snap = state.snapshot()
    assert snap["verdict"] == "granted"
    assert snap["name"] == "Alice"
    assert snap["is_door_open"] is True


def test_update_denied_door_not_open(state: SystemState):
    v = CurrentVerdict(verdict="denied", name="Unknown", score=0.3, access_type="unknown")
    state.update(v)
    assert state.snapshot()["is_door_open"] is False


def test_update_preserves_score_precision(state: SystemState):
    v = CurrentVerdict(verdict="granted", score=0.123456789)
    state.update(v)
    # to_dict() rounds to 4 decimal places
    assert state.snapshot()["score"] == round(0.123456789, 4)


def test_update_error_verdict(state: SystemState):
    v = CurrentVerdict(verdict="error")
    state.update(v)
    assert state.snapshot()["verdict"] == "error"
    assert state.snapshot()["is_door_open"] is False


# ---------------------------------------------------------------------------
# set_ml_health()
# ---------------------------------------------------------------------------


def test_set_ml_health_true(state: SystemState):
    state.set_ml_health(True)
    snap = state.snapshot()
    assert snap["ml_healthy"] is True
    assert snap["last_ml_check"] > 0


def test_set_ml_health_false_after_true(state: SystemState):
    state.set_ml_health(True)
    state.set_ml_health(False)
    assert state.snapshot()["ml_healthy"] is False


def test_set_ml_health_updates_timestamp(state: SystemState):
    before = time.time()
    state.set_ml_health(True)
    after = time.time()
    ts = state.snapshot()["last_ml_check"]
    assert before <= ts <= after


# ---------------------------------------------------------------------------
# CurrentVerdict.to_dict()
# ---------------------------------------------------------------------------


def test_current_verdict_to_dict_structure():
    v = CurrentVerdict(
        verdict="scanning", name="Bob", score=0.5, access_type="user", matched_user_id=7
    )
    d = v.to_dict()
    assert d["verdict"] == "scanning"
    assert d["name"] == "Bob"
    assert d["access_type"] == "user"
    assert d["matched_user_id"] == 7
    assert "timestamp" in d


def test_current_verdict_timestamp_is_iso(state: SystemState):
    v = CurrentVerdict(verdict="idle")
    d = v.to_dict()
    # Should parse without error
    from datetime import datetime

    datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00"))


# ---------------------------------------------------------------------------
# subscribe() / unsubscribe()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_subscriber_receives_update(state: SystemState):
    q = await state.subscribe()
    v = CurrentVerdict(verdict="granted", name="Alice")
    state.update(v)

    msg = await asyncio.wait_for(q.get(), timeout=1.0)
    assert msg["verdict"] == "granted"
    assert msg["name"] == "Alice"
    state.unsubscribe(q)


@pytest.mark.asyncio
async def test_unsubscribe_stops_delivery(state: SystemState):
    q = await state.subscribe()
    state.unsubscribe(q)

    state.update(CurrentVerdict(verdict="denied"))
    assert q.empty()


@pytest.mark.asyncio
async def test_multiple_subscribers_all_receive(state: SystemState):
    q1 = await state.subscribe()
    q2 = await state.subscribe()

    state.update(CurrentVerdict(verdict="idle"))

    msg1 = await asyncio.wait_for(q1.get(), timeout=1.0)
    msg2 = await asyncio.wait_for(q2.get(), timeout=1.0)
    assert msg1["verdict"] == "idle"
    assert msg2["verdict"] == "idle"

    state.unsubscribe(q1)
    state.unsubscribe(q2)
