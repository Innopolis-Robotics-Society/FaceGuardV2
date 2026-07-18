# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- LED status indicators (`app/leds.py`): green on access granted, red on access denied, yellow while a liveness check is pending, all off when idle. Real GPIO on Raspberry Pi (`LED_MODE=gpio`) or logged/emulated elsewhere. Configurable via `LED_MODE`, `LED_GREEN_PIN`, `LED_RED_PIN`, `LED_YELLOW_PIN`, `LED_GRANT_DURATION_SEC`.

### Changed
- Redesigned the admin UI (login, dashboard, users list) for better color consistency, readability, and layout.
- Optimized ML service background processing on Raspberry Pi.
- Iterated again on the liveness-detection landmark model to improve blink-detection accuracy.

### Fixed
- Fixed Delete/Revoke button sizing, alignment, and column layout in the users table.
- Fixed login navigation, video letterboxing, access-type toggle, and logout alignment issues.
- Fixed a blink-counter bug in liveness detection.
- Cleaned up backend code and miscellaneous frontend bugs.

## [2.1.0] - 2026-07-12
[2.1.0]: https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/tag/v2.1.0

### Added
- Nothing

### Changed
- Optimizing product so that video stream in ruspberry pi 4 24 fps

### Fixed
- Fixed liveness detection so that it`s a passive and faster

## [2.0.0] - 2026-07-05
[2.0.0]: https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/tag/v2.0.0
### Added
- **Issue #76**: Unified users + guests into a single `users` table with
  `type` ('permanent' | 'temporary') and nullable `expires_at`. Full CRUD
  via `FaceDatabase.update_user()` + type switching (permanent <-> temporary).
  Legacy two-table DBs are auto-migrated on startup.
- **Issue #77**: New HTML page `/users/{id}` with user details, edit form,
  and last 50 audit-log entries for that user. Main `/users` list now links
  to detail pages.
- **Issue #78**: New JSON API: `GET /backend/users`, `GET /backend/users/{id}`,
  `PUT /backend/users/{id}`, `DELETE /backend/users/{id}`. Full validation
  (type, expires_at, embedding size, duplicate names).
- **Issue #79**: Audit-log rotation (`purge_old_logs(days=30)`) — runs on
  startup + every 24h. `recognize()` now logs state transitions only
  (5-10x log reduction). ML service log level set to WARNING;
  `GET /health` filtered out of access logs.
- New tests: `tests/test_crud.py` (30 unit tests for unified schema, CRUD,
  type switching, log rotation, transition-only logging) and
  `tests/test_crud_api.py` (21 integration tests for the new API endpoints
  and HTML detail page).

### Changed
- Changed model on bufallo_sc instead of bufallo_l in ml_service/main.py 
- `FaceDatabase.recognize()` now writes audit log entries only on state
  transitions (verdict change or matched-name change). Pass
  `log_transitions_only=False` to force per-call logging.
- ML service (`ml_service/main.py`, `ml_stub/main.py`) runs with
  uvicorn `--log-level warning` and filters `GET /health` out of access
  logs (issue #79).
- `RecognitionLoop` runs a daily `purge_old_logs(30)` to enforce log
  retention policy.
- Root `README.md` documents the new endpoints and migration behavior.

### Fixed
- Fixed bugs either in backend and ml_service
- Deleted redundant dependencies in backend


## [1.1.0] - 2026-06-28
[1.1.0]: https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/tag/v1.1.0

### Added
- GitHub Actions CI pipeline (`.github/workflows/ci.yml`) with 5 jobs:
  lint/type check, Docker build, test + coverage, quality requirement
  tests (QRT), and dependency vulnerability scan (`pip-audit`).
- `pyproject.toml` — pytest markers (`integration`, `qrt`), coverage
  config, and dev dependencies (`pytest-cov`, `ruff`, `mypy`, `pip-audit`).
- `tests/test_config.py` — unit tests for critical configuration module.
- `tests/test_recognition.py` — unit tests for recognition loop
  construction and core tick logic (ML health, idle, granted states).
- `tests/test_integration.py` — integration tests for FastAPI routes
  (healthz, login form, login/logout flow) with TestClient.
- `docs/quality-requirements.md` — 5 quality requirements (QR-001…QR-005)
  traceable to user stories.
- `docs/quality-requirement-tests.md` — traceability matrix QR→QRT→test
  function.
- `docs/testing.md` — canonical testing status artifact with critical
  modules coverage, CI gate status, and additional QA check rationale.
- `docs/user-acceptance-tests.md` — 5 UAT scenarios for US-002, US-006/007,
  US-008/011, US-010, US-013.
- `@pytest.mark.qrt` annotations on existing tests for automated quality
  requirement test execution.

### Changed
- `tests/conftest.py` — replaced with TestClient fixture and mocked
  lifespan (ML client, recognition loop) for isolated integration testing.
- `pyproject.toml` — added `[build-system]` and `[tool.setuptools.packages]`
  to fix editable install in CI.
- Definition of Done updated to require green CI, ≥30% coverage on
  critical modules, and passing QRTs before marking PBI Done.

### Fixed
- `SERVO_OPEN_DURATION_SEC` test value increased from 0.05 to 0.1 s to
  satisfy pydantic `ge=0.1` validator.
- `tests/test_database.py` — replaced blind `Exception` with specific
  `sqlite3.IntegrityError` in duplicate user test.


## [1.0.0] - 2026-06-21
[1.0.0]: https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/tag/v1.0.0

### Added
- `MVP_v1/` — FastAPI backend with SQLite data access layer, session-based
  admin auth, web admin UI (Jinja2 + HTMX + Pico.css), MJPEG stream proxy,
  SSE live status, servo abstraction (`gpio` on Pi, `emulated` on x86),
  ML service HTTP client, recognition background loop.
- `MVP_v1/ml_stub/` — offline ML service stub for local development.
- `MVP_v1/tests/` — 28 unit tests (database, auth, servo).
- `docs/interface.md` rewritten: Admin CLI replaced by Web Admin UI.
- Docker Compose stack with `backend` + `ml` (stub) services.

### Changed
- Root `README.md` — added MVP v1 section with quick-start for both local
  dev and Raspberry Pi deployment.
- Root `.gitignore` — added `.pytest_cache/`, `.ruff_cache/`, `*.db-wal`,
  `*.db-shm`, `dist/`, `build/`.
- Root `.env.example` — references `MVP_v1/.env.example` for the full
  backend config.

## [0.0.0] - 2026-06-12
[0.0.0]: https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/tag/v0.0.0

### Added
- Initial project layout and requirements documentation.
- Prototype face-detection script using OpenCV layout emulation.
