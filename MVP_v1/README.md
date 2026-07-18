# FaceGuard Backend (MVP v1)

Web admin + recognition orchestration for the **FaceGuardV2** face-recognition
access-control system. Runs on Raspberry Pi 4 (Raspberry Pi OS) and on x86
laptops for development.

This directory is part of the FaceGuardV2 monorepo. Historical prototype
code lives in `../MVP_v0/`. Weekly course reports live in `../reports/`.

**For setup, deployment, and usage instructions, see the product documentation in [`../docs/`](../docs/):**

| Need | Document |
|---|---|
| Quick local demo | [`../docs/getting-started.md`](../docs/getting-started.md) |
| Raspberry Pi deployment | [`../docs/deployment-raspberry-pi.md`](../docs/deployment-raspberry-pi.md) |
| How the system is put together | [`../docs/architecture.md`](../docs/architecture.md) |
| Environment variables | [`../docs/configuration.md`](../docs/configuration.md) |
| Using the admin UI | [`../docs/user-guide.md`](../docs/user-guide.md) |
| Fixing a problem | [`../docs/troubleshooting.md`](../docs/troubleshooting.md) |

This README covers what's specific to working in this directory as a developer: project layout, running tests, and the internal ML-service integration contract.

---

## Project layout

```
MVP_v1/
├── app/
│   ├── main.py               # FastAPI app + lifespan
│   ├── config.py             # pydantic-settings from env
│   ├── database.py           # FaceDatabase — the only module that touches SQL
│   ├── schema.py             # loads schema.sql
│   ├── schema.sql            # SQLite DDL (unified users table, logs, admins)
│   ├── auth.py                # session auth + bcrypt
│   ├── ml_client.py          # async HTTP client to the ML service
│   ├── servo.py               # GpioServo + EmulatedServo
│   ├── state.py               # in-memory verdict state + SSE pub/sub
│   ├── recognition.py        # background poller + register_one()
│   ├── jinja.py                # Jinja2 environment setup
│   ├── routes/
│   │   ├── auth.py            # /login, /logout
│   │   ├── pages.py           # /, /users, /register, /logs, /users/{id}
│   │   ├── stream.py          # /stream (MJPEG proxy)
│   │   ├── status.py          # /status/events (SSE), /status/snapshot
│   │   ├── users.py           # CRUD + /register POST, /backend/users JSON API
│   │   └── logs.py            # /api/logs JSON
│   ├── templates/             # Jinja2 templates + partials/
│   └── static/                 # custom.css, dashboard.js
├── ml_service/
│   ├── main.py                # camera, InsightFace, ONNX PFLD liveness
│   ├── requirements.txt
│   └── Dockerfile
├── tests/                     # pytest suite (unit, integration, qrt markers)
├── data/                      # bind-mounted SQLite file (gitignored)
├── Dockerfile                 # backend image (multi-arch: arm64/amd64)
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── pyproject.toml
```

## Quick start for development

```bash
cd MVP_v1
cp .env.example .env
docker compose up --build
```

- Backend: http://localhost:8000
- ML service: http://localhost:8001 (internal, not user-facing)

Or run both processes directly without Docker (two terminals):

```bash
# Terminal 1 — ML service
pip install -r ml_service/requirements.txt
uvicorn ml_service.main:app --port 8001

# Terminal 2 — backend
pip install -r requirements.txt
export ML_SERVICE_URL=http://localhost:8001
uvicorn app.main:app --reload --port 8000
```

See [`../docs/getting-started.md`](../docs/getting-started.md) for the full first-run walkthrough and [`../docs/configuration.md`](../docs/configuration.md) for every environment variable.

## Database schema

See [`app/schema.sql`](app/schema.sql). As of v2.0.0, permanent users and temporary guests share one `users` table (`type` column, nullable `expires_at`), rather than separate `users`/`guests` tables. All access goes through `app/database.py:FaceDatabase` — no other module in the codebase touches SQL directly.

## Development

```bash
# Install dev deps
pip install -r requirements.txt pytest pytest-asyncio pytest-cov ruff mypy

# Run tests
pytest

# Lint
ruff check app/ ml_service/ tests/
ruff format --check app/ ml_service/ tests/

# Type check
mypy app/
```

Pytest markers: `integration` (routes + DB via `TestClient`), `qrt` (quality-requirement tests — see [`../docs/quality-requirement-tests.md`](../docs/quality-requirement-tests.md), a course QA artifact). Run just the unit suite with `pytest -m "not integration and not qrt"`.

## Integration contract with the ML service

The backend depends on the ML service exposing:

```
GET /health
  -> 200 {"status": "ok"}

GET /ml/latest
  -> 200 {
       "timestamp": "<ISO8601 UTC>",
       "faces": [
         {
           "bbox": [x1, y1, x2, y2],
           "embedding": [512 floats],     # L2-normalized
           "confidence": 0.0..1.0,
           "liveness_passed": true
         },
         ...
       ]
     }

GET /ml/stream
  -> 200, Content-Type: multipart/x-mixed-replace; boundary=frame
     body: stream of JPEG frames wrapped in multipart chunks
```

The ML service is the sole owner of the camera. The backend never opens `/dev/video0` directly — see [`../docs/architecture.md`](../docs/architecture.md) for why.

## Known limitations

- **No LED indicators** — wiring is straightforward but not yet implemented in the backend (planned; the dashboard verdict colors mirror the intended LED scheme).
- **Single admin** — multi-admin management isn't built yet; additional admins currently require inserting directly via `FaceDatabase.add_admin()`.
- **No HTTPS termination** — put a reverse proxy in front if exposed beyond a trusted local network.

## License

MIT — see [LICENSE](../LICENSE) in the repository root.
