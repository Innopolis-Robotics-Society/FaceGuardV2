# FaceGuard Backend (MVP v1)

Web admin + recognition orchestration for the **FaceGuardV2** face-recognition
access control system. Runs on Raspberry Pi 4 (Raspberry Pi OS) and on x86
laptops for development.

This directory is part of the FaceGuardV2 monorepo. Historical prototype
code lives in `../MVP_v0/`. Weekly reports live in `../reports/`. See the
root `../README.md` for project-level overview.


> **Scope of this module (Part 8, MVP v1, MUST HAVE only):**
> - US-02 — User registration (5-frame capture → averaged embedding → SQLite).
> - US-06 / US-07 — Servo actuation (GPIO on Pi, emulated on x86).
> - US-08 — Threshold via env (`THRESHOLD`).
> - US-01 — Recognition pipeline orchestration: backend owns all comparison
>   logic, ML service owns the camera + embedding extraction.
>
> Bonus and Should-Have stories (US-03 guest expiry, US-05 UI polish, US-09
> liveness, US-10 audit log) are partly included as supporting infrastructure
> but are not the focus of this MVP slice.

---

## Architecture

```
                ┌────────────────────┐         ┌────────────────────┐
   Admin laptop │                    │  MJPEG  │   ML service       │
   (LAN)  ────▶ │   FastAPI backend  │ ◀────── │   (camera +        │
                │   - SQLite         │  JSON   │    InsightFace)    │
                │   - Servo abstr.   │ ◀────── │                    │
                │   - SSE status     │         └────────────────────┘
                └─────────┬──────────┘                   │
                          │ GPIO (on Pi)                  │
                          ▼                              ▼
                    ┌─────────────┐               ┌──────────────┐
                    │   Servo     │               │  Raspberry Pi│
                    │   + LED     │               │  camera v1   │
                    └─────────────┘               └──────────────┘
```

**Responsibilities:**

| Layer                | Owner              | What it does                                   |
|----------------------|--------------------|------------------------------------------------|
| Camera capture       | ML service         | `cv2.VideoCapture`, frame annotation            |
| Face detection       | ML service         | InsightFace `buffalo_l`                         |
| Embedding extraction | ML service         | 512-dim L2-normalized vectors                   |
| **Embedding storage**| **Backend**        | SQLite, `users` + `guests` + `logs` tables      |
| **Comparison logic** | **Backend**        | cosine similarity against DB, threshold match   |
| **Access decision**  | **Backend**        | match / unknown, audit log                      |
| **Servo actuation**  | **Backend**        | GPIO on Pi, emulated on x86                     |
| Admin UI             | Backend            | Jinja2 + HTMX + Pico.css, session auth          |

The backend never opens the camera directly — that's the ML service's job.
Communication:

- `GET /ml/stream` (ML service) → proxied to browsers at `/stream` (backend).
- `GET /ml/latest` (ML service) → polled by the backend's recognition loop
  every `RECOGNITION_INTERVAL_MS` ms; returns `{faces: [{bbox, embedding, confidence}]}`.

---

## Quick start (local, with ML stub)

1. **Clone & enter the repo** (you already did).

2. **Copy env file & adjust:**

   ```bash
   cp .env.example .env
   # Generate a random SECRET_KEY:
   python -c "import secrets; print(secrets.token_hex(32))" | xargs -I{} sed -i 's/SECRET_KEY=.*/SECRET_KEY={}/' .env
   ```

3. **Run with Docker Compose:**

   ```bash
   docker compose up --build
   ```

   - Backend: http://localhost:8000
   - ML service: http://localhost:8001 (not user-facing)
   - Default login: `admin` / `change-me-on-first-login` (set in `.env`)

4. **Or run without Docker** (two terminals):

   ```bash
   # Terminal 1 — ML service
   pip install -r ml_service/requirements.txt
   uvicorn ml_service.main:app --port 8001

   # Terminal 2 — backend
   pip install -r requirements.txt
   export ML_SERVICE_URL=http://localhost:8001
   uvicorn app.main:app --reload --port 8000
   ```

---

## Running on Raspberry Pi 4

1. Install Docker:

   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   # log out and back in
   ```

2. Clone this repo onto the Pi.

3. Edit `.env`:

   ```ini
   SERVO_MODE=gpio
   SERVO_PIN=18                 # BCM pin
   SERVO_OPEN_DURATION_SEC=2.0
   THRESHOLD=0.45               # tune on real data (US-08)
   ADMIN_PASSWORD=<something-strong>
   SECRET_KEY=<random-32-bytes>
   ```

4. If using the **real ML service** (replace the stub):

   ```yaml
   # docker-compose.yml
   services:
     ml:
       image: <your-team-ml-image>:latest
       devices:
         - /dev/video0:/dev/video0
   ```

5. Wire the servo:

   | Servo wire | Pi GPIO      |
   |------------|--------------|
   | signal     | BCM 18 (pin 12) |
   | VCC        | 5V (pin 2 or 4) |
   | GND        | GND (pin 6)  |

6. Start:

   ```bash
   docker compose up -d --build
   ```

7. From another device on the same LAN, open
   `http://<pi-ip>:8000/` and log in as admin.

---

## User flows

### Admin login

1. Open `http://<host>:8000/login`.
2. Enter admin username + password (env-configured; first login uses
   `ADMIN_PASSWORD`, after which the password is bcrypt-hashed in SQLite).
3. Session cookie valid for 12h.

### Register a new person (US-02)

1. Open `/register`.
2. The live camera preview loads in the left panel (MJPEG from `/stream`).
3. Fill the form:
   - **Full name** — `Surname Firstname`, must be unique among permanent users.
   - **Access type** — `Permanent` or `Temporary` (with `Valid for N days`).
4. Click **Capture & register**.
5. Backend calls ML service 5 times (`REGISTRATION_FRAME_COUNT`), each
   ~`REGISTRATION_FRAME_INTERVAL_MS` ms apart, picks the biggest face,
   averages the 5 embeddings, L2-normalizes, and saves to SQLite.
6. HTMX swaps in a success/error partial — no full page reload.

### Live dashboard

- `/` shows the camera stream with an overlay reflecting the current
  verdict (`granted` / `denied` / `scanning` / `idle` / `error`).
- The right panel shows ML health, door state, last user, score, and DB
  counts. Updates push via SSE (`/status/events`).
- When access is granted, the backend triggers the servo (real GPIO on Pi,
  emulated on x86) for `SERVO_OPEN_DURATION_SEC` seconds.

### View logs (US-10)

- `/logs` lists the last 300 access attempts with score, type, and result.
- Filter by name substring and/or "today only".

### CRUD users & guests

- `/users` lists permanent users and active guests with delete/revoke buttons.
- Expired guests are auto-purged inside `recognize()` — no cron job needed.

---

## Configuration

All configuration is via environment variables (`.env`). See
[`.env.example`](.env.example) for the full list with comments.

| Variable                       | Default                          | Purpose                                  |
|--------------------------------|----------------------------------|------------------------------------------|
| `THRESHOLD`                    | `0.45`                           | Cosine similarity threshold (US-08)      |
| `RECOGNITION_INTERVAL_MS`      | `500`                            | ML poll interval                         |
| `REGISTRATION_FRAME_COUNT`     | `5`                              | Frames captured per registration         |
| `REGISTRATION_FRAME_INTERVAL_MS`| `400`                           | Delay between registration frames        |
| `DATABASE_PATH`                | `/data/faces.db`                 | SQLite file path                         |
| `ML_SERVICE_URL`               | `http://ml:8001`                 | Base URL of ML service                   |
| `ADMIN_USERNAME`               | `admin`                          | Bootstrap admin username                 |
| `ADMIN_PASSWORD`               | `change-me-on-first-login`       | Bootstrap admin password (plaintext)     |
| `ADMIN_PASSWORD_HASH`          | *(unset)*                        | Pre-hashed bcrypt password (preferred)   |
| `SECRET_KEY`                   | *(must override)*                | Session cookie signing key               |
| `SERVO_MODE`                   | `emulated`                       | `gpio` on Pi, `emulated` on x86          |
| `SERVO_PIN`                    | `18`                             | BCM pin for servo signal                 |
| `SERVO_OPEN_DURATION_SEC`      | `2.0`                            | How long the door stays "open"           |
| `HOST` / `PORT`                | `0.0.0.0` / `8000`               | uvicorn bind                             |

---

## Database schema

See [`app/schema.sql`](app/schema.sql). Three tables:

- `users(id, name UNIQUE, embedding BLOB, created_at)` — permanent users.
- `guests(id, name, embedding BLOB, expires_at)` — temporary access. **No
  `created_by` / `created_at` columns** (team decision). Auto-purged inside
  `recognize()` when `expires_at < now`.
- `logs(id, name, score, access_type, success, timestamp)` — audit trail.
- `admins(id, username, password_hash, created_at)` — web UI login.

All access goes through `app/database.py:FaceDatabase` (issue #29) — no
other module in the codebase touches SQL directly.

---

## Project layout

```
faceguard-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + lifespan
│   ├── config.py            # pydantic-settings from env
│   ├── database.py          # ★ FaceDatabase — issue #29 (data access layer)
│   ├── schema.py            # path to schema.sql
│   ├── schema.sql           # SQLite DDL
│   ├── auth.py              # session auth + bcrypt
│   ├── ml_client.py         # async HTTP client to ML service
│   ├── servo.py             # GpioServo + EmulatedServo (US-06/US-07)
│   ├── state.py             # in-memory verdict + SSE pub/sub
│   ├── recognition.py       # background poller + register_one()
│   ├── routes/
│   │   ├── auth.py          # /login, /logout
│   │   ├── pages.py         # /, /users, /register, /logs
│   │   ├── stream.py        # /stream (MJPEG proxy)
│   │   ├── status.py        # /status/events (SSE), /status/snapshot
│   │   ├── users.py         # CRUD + /register POST
│   │   └── logs.py          # /api/logs JSON
│   ├── templates/           # Jinja2
│   └── static/              # custom.css, dashboard.js
│   ├── main.py
│   └── requirements.txt
├── tests/                   # pytest suite
├── docs/
│   └── interface.md         # UI contract (web admin, replaces CLI)
├── Dockerfile               # backend image (multi-arch)
├── Dockerfile.ml-stub       # dev ML stub image
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── pyproject.toml
└── README.md
```

---

## API summary

| Method | Path                         | Auth | Purpose                          |
|--------|------------------------------|------|----------------------------------|
| GET    | `/login`                     | —    | Login form                       |
| POST   | `/login`                     | —    | Submit credentials               |
| POST   | `/logout`                    | ✓    | End session                      |
| GET    | `/`                          | ✓    | Live dashboard                   |
| GET    | `/users`                     | ✓    | Users + guests list              |
| POST   | `/users/{id}/delete`         | ✓    | Delete permanent user            |
| POST   | `/guests/{id}/delete`        | ✓    | Revoke guest                     |
| POST   | `/guests/purge`              | ✓    | Force-purge expired guests       |
| GET    | `/register`                  | ✓    | Registration form                |
| POST   | `/register`                  | ✓    | Capture 5 frames → save          |
| GET    | `/register/options/{kind}`   | ✓    | HTMX partial for access-type     |
| GET    | `/logs`                      | ✓    | HTML audit log                   |
| GET    | `/api/logs`                  | ✓    | JSON audit log                   |
| GET    | `/stream`                    | ✓    | MJPEG camera stream              |
| GET    | `/status/events`             | ✓    | SSE verdict stream               |
| GET    | `/status/snapshot`           | ✓    | One-shot status JSON             |
| GET    | `/healthz`                   | —    | Health probe                     |

---

## Development

```bash
# Install dev deps
pip install -r requirements.txt pytest pytest-asyncio

# Run tests
pytest

# Lint (optional)
ruff check app/ ml_service/ tests/
```

---

## Integration contract with the ML service

The real ML service (built by another team member) **must** expose:

```
GET /health
  -> 200 {"status": "ok"}

GET /ml/latest
  -> 200 {
       "timestamp": "<ISO8601 UTC>",
       "faces": [
         {
           "bbox": [x1, y1, x2, y2],         # pixel coords
           "embedding": [512 floats],        # L2-normalized
           "confidence": 0.0..1.0            # detection confidence
         },
         ...
       ]
     }

GET /ml/stream
  -> 200, Content-Type: multipart/x-mixed-replace; boundary=frame
     body: stream of JPEG frames wrapped in multipart chunks
```

The ML service is the **sole** owner of the camera. The backend never
opens `/dev/video0`.

---

## Known limitations (MVP v1 scope)

- **No liveness detection** (US-09 — bonus, out of MUST HAVE scope).
- **No LED indicators** — wiring documented but not yet implemented in the
  backend (planned for v2).
- **Single admin** — multi-role / multi-admin UI not built yet; new admins
  must be inserted directly via `FaceDatabase.add_admin()`.
- **No HTTPS termination** — assumed to be behind a reverse proxy on the Pi
  for production.

---

## License

MIT — see [LICENSE](../LICENSE) in the repository root.

---

## Issues #76 / #77 / #78 / #79 — latest changes

### Issue #76 — Unified user table + CRUD + type switching

The schema was previously split into two tables: `users` (permanent) and
`guests` (temporary). They are now unified into a single `users` table:

```sql
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT UNIQUE NOT NULL,
    embedding   BLOB NOT NULL,
    type        TEXT NOT NULL DEFAULT 'permanent'
                CHECK(type IN ('permanent', 'temporary')),
    expires_at  TIMESTAMP,                   -- NULL for permanent
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**New DB methods:**
- `register_user(name, embedding, type='permanent', expires_at=None)`
- `update_user(user_id, *, name=None, type=None, expires_at=None, embedding=None)`
- `list_users(type_filter=None, include_expired=True)`
- `purge_expired()` — replaces `purge_expired_guests()`
- Backward-compat wrappers: `register_guest`, `register_guest_for_days`,
  `list_guests`, `get_guest`, `delete_guest` — all delegate to the
  unified API.

### Issue #78 — PUT / GET JSON API

New JSON endpoints under `/backend/users[/{id}]`:

| Method | Path                       | Body                       | Returns                 |
|--------|----------------------------|----------------------------|-------------------------|
| GET    | `/backend/users`           | `?type=&include_expired=`  | `{users: [...]}`        |
| GET    | `/backend/users/{id}`      | —                          | user dict / 404         |
| PUT    | `/backend/users/{id}`      | `{name?, type?, expires_at?, embedding?}` | updated user |
| DELETE | `/backend/users/{id}`      | —                          | `{deleted: id}` / 404   |

PUT validation:
- `type` must be `'permanent'` or `'temporary'`.
- `expires_at` is required when switching to `temporary` (unless the
  user already has a future `expires_at`).
- `embedding` must be a list of exactly 512 floats.
- Duplicate `name` returns 409.
- Nonexistent `user_id` returns 404.

### Issue #77 — User detail + edit page

New HTML page at `/users/{id}`:
- Shows name, type (with badge), expiration (if temporary), creation date.
- Edit form with name + access type + expiration date picker.
- The expiration field is shown/hidden automatically based on the
  selected access type (small JS snippet).
- "Danger zone" with delete button.
- Right panel shows the last 50 audit-log entries for this user.

The main `/users` list now links each user name to its detail page.

Form submissions go to `POST /users/{id}/update` which forwards to
`db.update_user()` and redirects back to the detail page.

### Issue #79 — Logging cleanup

**ML service (`ml_service/main.py`):**
- uvicorn `--log-level warning` (set both in code and Dockerfiles).
- Custom `_HealthFilter` removes `GET /health` lines from the access log.

**Backend:**
- New `FaceDatabase.purge_old_logs(days=30)` deletes audit entries
  older than 30 days. Called on startup and then once every 24h from
  the recognition loop. Retention is configurable via
  `LOG_RETENTION_DAYS` env var.
- `recognize()` now tracks the last `(access_type, name)` state and
  writes a log row **only on state transitions**. Repeated identical
  verdicts no longer flood the audit log. Pass
  `log_transitions_only=False` to force per-call logging (used in some
  unit tests).
- Python-level `log.info("Denied: ...")` / `log.info("Granted: ...")`
  in `recognition.py` are also state-transition only.

End-to-end smoke check: with the recognition loop polling at 500ms, the
backend log now produces a single `Denied` line when the camera sees an
unknown face — previously it produced 2 such lines per second.
