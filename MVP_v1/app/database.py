"""Centralized data access layer for FaceGuard.

This module is the only place in the codebase that knows about SQL. All
other modules call the typed methods of ``FaceDatabase`` and never see a
raw query, cursor, or BLOB. This keeps the schema swappable (we could
move to PostgreSQL later by editing this file only) and gives us a
single seam to add caching, logging, or transactions.

Schema lives in ``app/schema.sql`` and is applied idempotently on startup.
"""

from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

import numpy as np

from .schema import SCHEMA_PATH

AccessType = Literal["user", "guest", "unknown"]
UserType = Literal["permanent", "temporary"]


# ---------------------------------------------------------------------------
# Row dataclasses — structured results returned to the rest of the app.
# No Cursor, no tuple indexing, no BLOB leaks.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class User:
    """A registered user.

    ``type`` is ``'permanent'`` or ``'temporary'``. ``expires_at`` is
    ``None`` for permanent users and a timezone-aware datetime for
    temporary ones.
    """

    id: int
    name: str
    embedding: np.ndarray  # float32, (512,)
    type: UserType
    expires_at: datetime | None
    created_at: datetime


@dataclass(frozen=True)
class LogEntry:
    id: int
    name: str
    score: float | None
    access_type: AccessType
    success: bool
    timestamp: datetime
    liveness_passed: bool | None = None


@dataclass(frozen=True)
class Admin:
    id: int
    username: str
    password_hash: str
    created_at: datetime


@dataclass(frozen=True)
class RecognitionResult:
    """Outcome of a single ``recognize()`` call.

    When ``access_type == "unknown"``, no match above the threshold was
    found; ``name`` is then ``"Unknown"`` and ``score`` carries the best
    similarity observed (useful for audit logging of denied attempts).
    """

    name: str
    score: float
    access_type: AccessType
    matched_user_id: int | None = None


# ---------------------------------------------------------------------------
# Encoding helpers — embeddings are stored as float32 BLOBs.
# ---------------------------------------------------------------------------

_EMBEDDING_DTYPE = np.float32


def _encode_embedding(emb: np.ndarray) -> bytes:
    arr = np.asarray(emb, dtype=_EMBEDDING_DTYPE)
    if arr.ndim != 1:
        raise ValueError(f"embedding must be 1-D, got shape {arr.shape}")
    return arr.tobytes()


def _decode_embedding(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=_EMBEDDING_DTYPE).copy()


# ---------------------------------------------------------------------------
# Timestamp helpers — stored as ISO 8601 strings in UTC.
# ---------------------------------------------------------------------------


def _to_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat()


def _from_iso(value: str) -> datetime:
    """Parse an ISO 8601 string from SQLite into a timezone-aware datetime.

    SQLite's ``CURRENT_TIMESTAMP`` returns naive UTC strings like
    ``2026-06-12 14:32:11``, so we accept both that and full ISO format.
    """
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        # Fallback for SQLite's bare "YYYY-MM-DD HH:MM:SS" format.
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


# ---------------------------------------------------------------------------
# FaceDatabase — the single entry point to the data layer.
# ---------------------------------------------------------------------------


class FaceDatabase:
    """SQLite-backed data access layer for FaceGuard.

    Thread-safe: a single ``sqlite3.Connection`` guarded by a re-entrant
    lock. SQLite handles concurrent reads from multiple threads fine, but
    writes need serialization, so we serialize all access — the workload
    is tiny (50–100 rows) and correctness beats micro-optimization.
    """

    def __init__(self, db_path: str | Path = "data/faces.db"):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            str(self._db_path),
            check_same_thread=False,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._apply_schema()
        # Tracks the last recognize() outcome so we only log state
        # transitions (e.g. idle -> granted, granted -> denied) instead
        # of writing a row on every poll.
        self._last_recognize_state: tuple[str, str] | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _apply_schema(self) -> None:
        schema_sql = Path(SCHEMA_PATH).read_text(encoding="utf-8")
        self._conn.executescript(schema_sql)
        self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def __enter__(self) -> FaceDatabase:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Users — unified permanent + temporary
    # ------------------------------------------------------------------

    def register_user(
        self,
        name: str,
        embedding: np.ndarray,
        type: UserType = "permanent",
        expires_at: datetime | None = None,
    ) -> User:
        """Insert a user of the given type.

        For ``type='temporary'``, ``expires_at`` must be a timezone-aware
        datetime in the future. For ``type='permanent'``, ``expires_at``
        is ignored and stored as NULL.

        Raises ``sqlite3.IntegrityError`` if the name already exists.
        """
        if type not in ("permanent", "temporary"):
            raise ValueError(f"invalid user type: {type!r}")
        if type == "temporary":
            if expires_at is None:
                raise ValueError("temporary users require expires_at")
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=UTC)
        else:
            expires_at = None  # force NULL for permanent

        blob = _encode_embedding(embedding)
        expires_iso = _to_iso(expires_at) if expires_at else None
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO users (name, embedding, type, expires_at) VALUES (?, ?, ?, ?)",
                (name, blob, type, expires_iso),
            )
            self._conn.commit()
            return self.get_user(cur.lastrowid)  # type: ignore[arg-type]

    def get_user(self, user_id: int) -> User | None:
        with self._lock:
            row = self._conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return _row_to_user(row) if row else None

    def get_user_by_name(self, name: str) -> User | None:
        with self._lock:
            row = self._conn.execute("SELECT * FROM users WHERE name = ?", (name,)).fetchone()
        return _row_to_user(row) if row else None

    def list_users(
        self,
        type_filter: UserType | None = None,
        include_expired: bool = True,
    ) -> list[User]:
        """List users, optionally filtered by type and/or expiry.

        - ``type_filter=None`` returns both permanent and temporary.
        - ``include_expired=False`` excludes temporary users whose
          ``expires_at`` is in the past (permanent users are always included).
        """
        clauses: list[str] = []
        params: list[object] = []
        if type_filter is not None:
            clauses.append("type = ?")
            params.append(type_filter)
        if not include_expired:
            now_iso = _to_iso(datetime.now(UTC))
            clauses.append("(type = 'permanent' OR (type = 'temporary' AND expires_at > ?))")
            params.append(now_iso)

        query = "SELECT * FROM users"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY name ASC"

        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [_row_to_user(r) for r in rows]

    def update_user(
        self,
        user_id: int,
        *,
        name: str | None = None,
        type: UserType | None = None,
        expires_at: datetime | None | Literal["unset"] | None = None,
        embedding: np.ndarray | None = None,
    ) -> User | None:
        """Update one or more fields of a user.

        Returns the updated user, or ``None`` if ``user_id`` doesn't exist.

        Type-switching rules:
          * Switching to ``'permanent'`` clears ``expires_at`` (sets to NULL).
          * Switching to ``'temporary'`` requires ``expires_at`` to be
            provided (either in this call or already set in the DB).

        Pass ``expires_at=None`` together with ``type='temporary'`` to
        keep the existing ``expires_at``. To explicitly clear it, switch
        the type to ``'permanent'`` instead.

        Raises ``ValueError`` on invalid combinations.
        Raises ``sqlite3.IntegrityError`` if the new name conflicts with
        an existing user.
        """
        # Sentinel for "not provided" so we can distinguish from
        # ``expires_at=None`` (which means "clear it" when type=permanent).
        NOT_PROVIDED = object()
        if expires_at is None and type != "permanent":
            expires_at_arg = NOT_PROVIDED  # type: ignore[assignment]
        else:
            expires_at_arg = expires_at  # type: ignore[assignment]

        if type is not None and type not in ("permanent", "temporary"):
            raise ValueError(f"invalid user type: {type!r}")

        if expires_at_arg is not None and expires_at_arg is not NOT_PROVIDED:
            if not isinstance(expires_at_arg, datetime):  # type: ignore[unreachable]
                raise ValueError("expires_at must be a datetime")
            if expires_at_arg.tzinfo is None:  # type: ignore[union-attr]
                expires_at_arg = expires_at_arg.replace(tzinfo=UTC)  # type: ignore[union-attr]

        with self._lock:
            existing = self.get_user(user_id)
            if existing is None:
                return None

            new_type = type if type is not None else existing.type

            if new_type == "permanent":
                new_expires = None  # always clear for permanent
            else:
                if expires_at_arg is not None and expires_at_arg is not NOT_PROVIDED:
                    new_expires = expires_at_arg  # type: ignore[assignment]
                elif existing.expires_at is not None:
                    new_expires = existing.expires_at
                else:
                    raise ValueError("temporary user requires expires_at to be set")

            sets: list[str] = []
            params: list[object] = []
            if name is not None and name != existing.name:
                sets.append("name = ?")
                params.append(name)
            if type is not None and type != existing.type:
                sets.append("type = ?")
                params.append(type)
            sets.append("expires_at = ?")
            params.append(_to_iso(new_expires) if new_expires else None)
            if embedding is not None:
                sets.append("embedding = ?")
                params.append(_encode_embedding(embedding))

            if not sets:
                return existing

            params.append(user_id)
            self._conn.execute(
                f"UPDATE users SET {', '.join(sets)} WHERE id = ?",
                params,
            )
            self._conn.commit()
            return self.get_user(user_id)

    def delete_user(self, user_id: int) -> bool:
        with self._lock:
            cur = self._conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self._conn.commit()
            return cur.rowcount > 0

    def purge_expired(self) -> int:
        """Delete every temporary user whose ``expires_at`` is in the past.

        Returns the number of rows deleted. Called lazily by
        ``recognize()`` and periodically by the recognition loop.
        """
        now_iso = _to_iso(datetime.now(UTC))
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM users WHERE type = 'temporary' AND expires_at < ?",
                (now_iso,),
            )
            self._conn.commit()
            return cur.rowcount

    # ------------------------------------------------------------------
    # Backward compatibility — legacy guest API.
    #
    # These wrap the unified user API so that older code and tests
    # continue to work. New code should use register_user(type='temporary').
    # ------------------------------------------------------------------

    def register_guest(
        self,
        name: str,
        embedding: np.ndarray,
        expires_at: datetime,
    ) -> User:
        return self.register_user(name, embedding, type="temporary", expires_at=expires_at)

    def register_guest_for_days(
        self,
        name: str,
        embedding: np.ndarray,
        days: int,
    ) -> User:
        expires = datetime.now(UTC) + timedelta(days=days)
        return self.register_user(name, embedding, type="temporary", expires_at=expires)

    def get_guest(self, guest_id: int) -> User | None:
        return self.get_user(guest_id)

    def list_guests(self, include_expired: bool = False) -> list[User]:
        return self.list_users(type_filter="temporary", include_expired=include_expired)

    def delete_guest(self, guest_id: int) -> bool:
        return self.delete_user(guest_id)

    def purge_expired_guests(self) -> int:
        return self.purge_expired()

    # ------------------------------------------------------------------
    # Audit log
    # ------------------------------------------------------------------

    def add_log(
        self,
        name: str,
        score: float | None,
        access_type: AccessType,
        success: bool,
        liveness_passed: bool | None = None,
    ) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO logs (name, score, access_type, success, liveness_passed) VALUES (?, ?, ?, ?, ?)",
                (name, score, access_type, bool(success), liveness_passed),
            )
            self._conn.commit()

    def list_logs(
        self,
        limit: int = 200,
        today_only: bool = False,
        user_filter: str | None = None,
    ) -> list[LogEntry]:
        query = "SELECT * FROM logs"
        clauses: list[str] = []
        params: list[object] = []

        if today_only:
            clauses.append("DATE(timestamp) = DATE('now')")
        if user_filter:
            clauses.append("name LIKE ?")
            params.append(f"%{user_filter}%")

        if clauses:
            query += " WHERE " + " AND ".join(clauses)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [_row_to_log(r) for r in rows]

    def purge_old_logs(self, days: int = 30) -> int:
        """Delete log entries older than ``days`` days.

        Default retention is 30 days. Returns the number of rows deleted.
        """
        cutoff = datetime.now(UTC) - timedelta(days=days)
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM logs WHERE timestamp < ?",
                (_to_iso(cutoff),),
            )
            self._conn.commit()
            return cur.rowcount

    # ------------------------------------------------------------------
    # Recognition — the hot path.
    #
    # By default, audit logs are written only on state transitions
    # (verdict change OR matched-name change). This reduces log volume
    # 5–10x without losing security-relevant events. Pass
    # ``log_transitions_only=False`` to force a log entry on every call
    # (used by some tests).
    # ------------------------------------------------------------------

    def recognize(
        self,
        embedding: np.ndarray,
        threshold: float,
        *,
        log_transitions_only: bool = True,
    ) -> RecognitionResult:
        probe = np.asarray(embedding, dtype=_EMBEDDING_DTYPE)
        norm = float(np.linalg.norm(probe))
        if norm > 0:
            probe = probe / norm

        # 1. Lazy cleanup of expired temporary users.
        self.purge_expired()

        # 2. Load candidates — all permanent users + non-expired temporary.
        with self._lock:
            now_iso = _to_iso(datetime.now(UTC))
            rows = self._conn.execute(
                "SELECT id, name, embedding, type FROM users "
                "WHERE type = 'permanent' "
                "   OR (type = 'temporary' AND expires_at > ?)",
                (now_iso,),
            ).fetchall()

        best: RecognitionResult = RecognitionResult(
            name="Unknown",
            score=-1.0,
            access_type="unknown",
            matched_user_id=None,
        )

        # 3+4. Compare against all candidates (cosine sim via dot product,
        # since embeddings are L2-normalized at write time).
        for row in rows:
            cand = _decode_embedding(row["embedding"])
            score = float(np.dot(probe, cand))
            if score > best.score:
                access_type: AccessType = "user" if row["type"] == "permanent" else "guest"
                best = RecognitionResult(
                    name=row["name"],
                    score=score,
                    access_type=access_type,
                    matched_user_id=row["id"],
                )

        # 5. Apply threshold.
        matched = best.score >= threshold and best.access_type != "unknown"
        if not matched:
            result = RecognitionResult(
                name="Unknown",
                score=best.score if best.score >= 0 else 0.0,
                access_type="unknown",
                matched_user_id=None,
            )
        else:
            result = best

        # 6. Audit log — only on state transitions.
        new_state = (result.access_type, result.name)
        should_log = True
        if log_transitions_only and self._last_recognize_state == new_state:
            should_log = False
        self._last_recognize_state = new_state

        if should_log:
            self.add_log(
                name=result.name,
                score=result.score,
                access_type=result.access_type,
                success=matched,
            )

        return result

    def reset_recognize_state(self) -> None:
        """Clear the last-state tracker. Useful in tests."""
        self._last_recognize_state = None

    # ------------------------------------------------------------------
    # Admins
    # ------------------------------------------------------------------

    def add_admin(self, username: str, password_hash: str) -> Admin:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            self._conn.commit()
            return self.get_admin(cur.lastrowid)  # type: ignore[arg-type]

    def get_admin(self, admin_id: int) -> Admin | None:
        with self._lock:
            row = self._conn.execute("SELECT * FROM admins WHERE id = ?", (admin_id,)).fetchone()
        return _row_to_admin(row) if row else None

    def get_admin_by_username(self, username: str) -> Admin | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM admins WHERE username = ?", (username,)
            ).fetchone()
        return _row_to_admin(row) if row else None

    def bootstrap_admin(
        self,
        username: str,
        password_hash: str,
    ) -> Admin:
        """Idempotent: insert the admin only if no admin with this username
        exists yet. Returns the existing or newly created admin."""
        existing = self.get_admin_by_username(username)
        if existing:
            return existing
        return self.add_admin(username, password_hash)

    # ------------------------------------------------------------------
    # Misc — for health checks and the status endpoint.
    # ------------------------------------------------------------------

    def counts(self) -> dict[str, int]:
        with self._lock:
            permanent = self._conn.execute(
                "SELECT COUNT(*) AS n FROM users WHERE type = 'permanent'"
            ).fetchone()
            now_iso = _to_iso(datetime.now(UTC))
            active_temp = self._conn.execute(
                "SELECT COUNT(*) AS n FROM users WHERE type = 'temporary' AND expires_at > ?",
                (now_iso,),
            ).fetchone()
            logs = self._conn.execute("SELECT COUNT(*) AS n FROM logs").fetchone()
        return {
            "users": int(permanent["n"]),
            "active_guests": int(active_temp["n"]),
            "logs": int(logs["n"]),
        }


# ---------------------------------------------------------------------------
# Row → dataclass adapters. Kept private; the rest of the app never sees
# sqlite3.Row.
# ---------------------------------------------------------------------------


def _row_to_user(row: sqlite3.Row) -> User:
    expires_raw = row["expires_at"]
    return User(
        id=int(row["id"]),
        name=row["name"],
        embedding=_decode_embedding(row["embedding"]),
        type=row["type"],  # type: ignore[arg-type]
        expires_at=_from_iso(expires_raw) if expires_raw else None,
        created_at=_from_iso(row["created_at"]),
    )


def _row_to_log(row: sqlite3.Row) -> LogEntry:
    try:
        liveness = row["liveness_passed"]
        if liveness is not None:
            liveness = bool(liveness)
    except (IndexError, KeyError):
        liveness = None
    return LogEntry(
        id=int(row["id"]),
        name=row["name"],
        score=None if row["score"] is None else float(row["score"]),
        access_type=row["access_type"],
        success=bool(row["success"]),
        timestamp=_from_iso(row["timestamp"]),
        liveness_passed=liveness,
    )


def _row_to_admin(row: sqlite3.Row) -> Admin:
    return Admin(
        id=int(row["id"]),
        username=row["username"],
        password_hash=row["password_hash"],
        created_at=_from_iso(row["created_at"]),
    )


__all__ = [
    "AccessType",
    "Admin",
    "FaceDatabase",
    "LogEntry",
    "RecognitionResult",
    "User",
    "UserType",
]
