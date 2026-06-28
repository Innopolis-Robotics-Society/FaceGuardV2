# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed
- Changed model on bufallo_sc instead of bufallo_l in ml_service/main.py 

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
