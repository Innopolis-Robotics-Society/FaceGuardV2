"""Centralized data access layer for FaceGuard (issue #29).

This module is the *only* place in the codebase that knows about SQL.
Every other module (recognition loop, web routes, auth, registration
flow) calls the typed methods of `FaceDatabase` and never sees a raw
query, cursor, or BLOB. This keeps the schema swappable (we could move
to PostgreSQL later by editing this file only) and gives us a single
seam to add caching, logging, or transactions.

Schema lives in `app/schema.sql` and is applied idempotently on startup.
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


# ---------------------------------------------------------------------------
# Row dataclasses — structured results returned to the rest of the app.
# No Cursor, no tuple indexing, no BLOB leaks.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class User:
    id: int
    name: str
    embedding: np.ndarray  # float32, (512,)
    created_at: datetime


@dataclass(frozen=True)
class Guest:
    id: int
    name: str
    embedding: np.ndarray  # float32, (512,)
    expires_at: datetime


@dataclass(frozen=True)
class LogEntry:
    id: int
    name: str
    score: float | None
    access_type: AccessType
    success: bool
    timestamp: datetime


@dataclass(frozen=True)
class Admin:
    id: int
    username: str
    password_hash: str
    created_at: datetime


@dataclass(frozen=True)
class RecognitionResult:
    """Outcome of a single recognize() call.

    `access_type == "unknown"` means no match above threshold; in that case
    `name` is `"Unknown"` and `score` carries the best similarity we saw
    (useful for audit logging of denied attempts).
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

    SQLite's `CURRENT_TIMESTAMP` returns naive UTC strings like
    `2026-06-12 14:32:11`, so we accept both that and full ISO format.
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

    Thread-safe: a single `sqlite3.Connection` guarded by a re-entrant
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
    # Users (permanent)
    # ------------------------------------------------------------------

    def register_user(self, name: str, embedding: np.ndarray) -> User:
        """Insert a permanent user. Raises `sqlite3.IntegrityError` if the
        name already exists."""
        blob = _encode_embedding(embedding)
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO users (name, embedding) VALUES (?, ?)",
                (name, blob),
            )
            self._conn.commit()
            return self.get_user(cur.lastrowid)  # type: ignore[arg-type]

    def get_user(self, user_id: int) -> User | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return _row_to_user(row) if row else None

    def get_user_by_name(self, name: str) -> User | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM users WHERE name = ?",
                (name,),
            ).fetchone()
        return _row_to_user(row) if row else None

    def list_users(self) -> list[User]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM users ORDER BY name ASC"
            ).fetchall()
        return [_row_to_user(r) for r in rows]

    def delete_user(self, user_id: int) -> bool:
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM users WHERE id = ?", (user_id,)
            )
            self._conn.commit()
            return cur.rowcount > 0

    # ------------------------------------------------------------------
    # Guests (temporary)
    #
    # Per team decision: the guests table stores ONLY `expires_at`
    # (no `created_by`, no `created_at`). Expired guests are deleted
    # lazily inside `recognize()` and explicitly via `purge_expired_guests()`.
    # ------------------------------------------------------------------

    def register_guest(
        self,
        name: str,
        embedding: np.ndarray,
        expires_at: datetime,
    ) -> Guest:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        blob = _encode_embedding(embedding)
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO guests (name, embedding, expires_at) "
                "VALUES (?, ?, ?)",
                (name, blob, _to_iso(expires_at)),
            )
            self._conn.commit()
            return self.get_guest(cur.lastrowid)  # type: ignore[arg-type]

    def register_guest_for_days(
        self,
        name: str,
        embedding: np.ndarray,
        days: int,
    ) -> Guest:
        """Convenience: register a guest whose access expires in N days
        from now (UTC)."""
        expires = datetime.now(UTC) + timedelta(days=days)
        return self.register_guest(name, embedding, expires)

    def get_guest(self, guest_id: int) -> Guest | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM guests WHERE id = ?", (guest_id,)
            ).fetchone()
        return _row_to_guest(row) if row else None

    def list_guests(self, include_expired: bool = False) -> list[Guest]:
        with self._lock:
            if include_expired:
                rows = self._conn.execute(
                    "SELECT * FROM guests ORDER BY expires_at ASC"
                ).fetchall()
            else:
                now_iso = _to_iso(datetime.now(UTC))
                rows = self._conn.execute(
                    "SELECT * FROM guests WHERE expires_at > ? "
                    "ORDER BY expires_at ASC",
                    (now_iso,),
                ).fetchall()
        return [_row_to_guest(r) for r in rows]

    def delete_guest(self, guest_id: int) -> bool:
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM guests WHERE id = ?", (guest_id,)
            )
            self._conn.commit()
            return cur.rowcount > 0

    def purge_expired_guests(self) -> int:
        """Delete every guest whose `expires_at` is in the past.

        Returns the number of rows deleted. Called lazily by
        `recognize()` and periodically by the recognition loop.
        """
        now_iso = _to_iso(datetime.now(UTC))
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM guests WHERE expires_at < ?", (now_iso,)
            )
            self._conn.commit()
            return cur.rowcount

    # ------------------------------------------------------------------
    # Logs (US-10: audit log)
    # ------------------------------------------------------------------

    def add_log(
        self,
        name: str,
        score: float | None,
        access_type: AccessType,
        success: bool,
    ) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO logs (name, score, access_type, success) "
                "VALUES (?, ?, ?, ?)",
                (name, score, access_type, bool(success)),
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

    # ------------------------------------------------------------------
    # Recognition — the hot path.
    #
    # Steps:
    #   1. Purge expired guests (lazy cleanup, no background thread).
    #   2. Load every active candidate (users + non-expired guests).
    #   3. Compute cosine similarity (embeddings are L2-normalized at
    #      write time, so dot product == cosine).
    #   4. Pick the best candidate; if its score >= threshold, it's a
    #      match. Otherwise return Unknown with the best score for audit.
    #   5. Log the attempt to `logs`.
    # ------------------------------------------------------------------

    def recognize(
        self,
        embedding: np.ndarray,
        threshold: float,
    ) -> RecognitionResult:
        probe = np.asarray(embedding, dtype=_EMBEDDING_DTYPE)
        norm = float(np.linalg.norm(probe))
        if norm > 0:
            probe = probe / norm

        # 1. Lazy cleanup of expired guests.
        self.purge_expired_guests()

        # 2. Load candidates.
        with self._lock:
            user_rows = self._conn.execute(
                "SELECT id, name, embedding FROM users"
            ).fetchall()
            now_iso = _to_iso(datetime.now(UTC))
            guest_rows = self._conn.execute(
                "SELECT id, name, embedding FROM guests WHERE expires_at > ?",
                (now_iso,),
            ).fetchall()

        best: RecognitionResult = RecognitionResult(
            name="Unknown",
            score=-1.0,
            access_type="unknown",
            matched_user_id=None,
        )

        # 3+4. Compare against users.
        for row in user_rows:
            cand = _decode_embedding(row["embedding"])
            score = float(np.dot(probe, cand))
            if score > best.score:
                best = RecognitionResult(
                    name=row["name"],
                    score=score,
                    access_type="user",
                    matched_user_id=row["id"],
                )

        # 3+4. Compare against guests.
        for row in guest_rows:
            cand = _decode_embedding(row["embedding"])
            score = float(np.dot(probe, cand))
            if score > best.score:
                best = RecognitionResult(
                    name=row["name"],
                    score=score,
                    access_type="guest",
                    matched_user_id=row["id"],
                )

        # 5. Apply threshold.
        matched = best.score >= threshold and best.access_type != "unknown"
        if not matched:
            # Keep best score for the audit log, but mark as unknown.
            result = RecognitionResult(
                name="Unknown",
                score=best.score if best.score >= 0 else 0.0,
                access_type="unknown",
                matched_user_id=None,
            )
        else:
            result = best

        # 6. Audit log (always — both successes and denials).
        self.add_log(
            name=result.name,
            score=result.score,
            access_type=result.access_type,
            success=matched,
        )

        return result

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
            row = self._conn.execute(
                "SELECT * FROM admins WHERE id = ?", (admin_id,)
            ).fetchone()
        return _row_to_admin(row) if row else None

    def get_admin_by_username(self, username: str) -> Admin | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM admins WHERE username = ?", (username,)
            ).fetchone()
        return _row_to_admin(row) if row else None

    def list_admins(self) -> list[Admin]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM admins ORDER BY username ASC"
            ).fetchall()
        return [_row_to_admin(r) for r in rows]

    def count_admins(self) -> int:
        with self._lock:
            row = self._conn.execute("SELECT COUNT(*) AS n FROM admins").fetchone()
        return int(row["n"])

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
    # Misc — for health checks and status endpoint.
    # ------------------------------------------------------------------

    def counts(self) -> dict[str, int]:
        with self._lock:
            users = self._conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()
            guests = self._conn.execute(
                "SELECT COUNT(*) AS n FROM guests WHERE expires_at > ?",
                (_to_iso(datetime.now(UTC)),),
            ).fetchone()
            logs = self._conn.execute("SELECT COUNT(*) AS n FROM logs").fetchone()
        return {
            "users": int(users["n"]),
            "active_guests": int(guests["n"]),
            "logs": int(logs["n"]),
        }

    def vacuum(self) -> None:
        with self._lock:
            self._conn.execute("VACUUM")
            self._conn.commit()


# ---------------------------------------------------------------------------
# Row → dataclass adapters. Kept private; the rest of the app never sees
# sqlite3.Row.
# ---------------------------------------------------------------------------


def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        id=int(row["id"]),
        name=row["name"],
        embedding=_decode_embedding(row["embedding"]),
        created_at=_from_iso(row["created_at"]),
    )


def _row_to_guest(row: sqlite3.Row) -> Guest:
    return Guest(
        id=int(row["id"]),
        name=row["name"],
        embedding=_decode_embedding(row["embedding"]),
        expires_at=_from_iso(row["expires_at"]),
    )


def _row_to_log(row: sqlite3.Row) -> LogEntry:
    return LogEntry(
        id=int(row["id"]),
        name=row["name"],
        score=None if row["score"] is None else float(row["score"]),
        access_type=row["access_type"],  # type: ignore[arg-type]
        success=bool(row["success"]),
        timestamp=_from_iso(row["timestamp"]),
    )


def _row_to_admin(row: sqlite3.Row) -> Admin:
    return Admin(
        id=int(row["id"]),
        username=row["username"],
        password_hash=row["password_hash"],
        created_at=_from_iso(row["created_at"]),
    )


# Re-export the public surface.
__all__ = [
    "AccessType",
    "Admin",
    "FaceDatabase",
    "Guest",
    "LogEntry",
    "RecognitionResult",
    "User",
]
