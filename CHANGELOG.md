# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed


## [0.0.0] - 2026-06-12
### Added
- Initial project layout and requirements documentation.
- Prototype face-detection script using OpenCV layout emulation.

[0.0.0]: https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/tag/v0.0.0


## [Unreleased] - 2026-06-21

### Added
- Issue-Linked Workflow


### Changed

### Deprecated

### Removed

### Fixed

[1.0.0]: https://github.com/ORG/REPO/releases/tag/v1.0.0

## [Unreleased - MVP v1 backend]

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
