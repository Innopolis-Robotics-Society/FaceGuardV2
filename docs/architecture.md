# Architecture

FaceGuardV2 is a face-recognition access-control system for a single door. It is split into two runtime services plus the physical hardware they control:

```
                ┌────────────────────┐         ┌────────────────────┐
   Admin laptop │                    │  MJPEG  │   ML service       │
   (LAN)  ────▶ │   FastAPI backend  │ ◀────── │   (camera +        │
                │   - SQLite         │  JSON   │    InsightFace +   │
                │   - Servo control  │ ◀────── │    liveness check) │
                │   - SSE status     │         └──────────┬─────────┘
                └─────────┬──────────┘                    │
                          │ GPIO (Raspberry Pi only)       │ /dev/video0
                          ▼                                ▼
                    ┌─────────────┐               ┌──────────────────┐
                    │   Servo     │               │  Camera          │
                    │   (door)    │               │  (USB / Pi Cam)  │
                    └─────────────┘               └──────────────────┘
```

## Components and responsibilities

| Component | Owner | Responsibility |
|---|---|---|
| Camera capture | ML service | Opens `/dev/video0`, reads frames. |
| Face detection | ML service | InsightFace (`buffalo_sc` model). |
| Embedding extraction | ML service | 512-dimensional, L2-normalized face vectors. |
| Liveness / blink check | ML service | ONNX Runtime PFLD facial-landmark model, eye-aspect-ratio (EAR) blink detection, to resist photo/screen spoofing. |
| Embedding storage | Backend | SQLite, via a single data-access module. |
| Comparison / decision logic | Backend | Cosine similarity against stored embeddings, threshold check, expiry check for temporary access. |
| Access audit logging | Backend | Every recognition attempt (granted/denied/unknown) recorded. |
| Servo actuation | Backend | GPIO on Raspberry Pi, or emulated for development/demo. |
| Admin web UI | Backend | Server-rendered pages (Jinja2 + HTMX), session-authenticated. |

The backend never opens the camera directly — that boundary is intentional (see [ADR-001](architecture/adr/ADR-001-separate-backend-and-ml-service.md)) so the backend's recognition/decision logic can be developed and tested independently of camera/ML internals, and so the camera is a clearly isolated dependency in deployment.

## How the two services talk

The backend polls the ML service over plain internal HTTP (not exposed to end users):

- `GET /ml/latest` — polled every `RECOGNITION_INTERVAL_MS` (default 500ms). Returns detected faces with bounding boxes, embeddings, detection confidence, and liveness status.
- `GET /ml/stream` — an MJPEG multipart stream, proxied by the backend to the browser at `/stream` so the live camera feed can be shown in the dashboard without the browser talking to the ML service directly.
- `GET /health` — used by the backend to report ML service availability in the dashboard status panel.

## Request flow: registering a new person

1. Admin fills in the `/register` form (name, permanent or temporary access) and submits.
2. Backend validates the admin session.
3. Backend requests `REGISTRATION_FRAME_COUNT` (default 5) frames from the ML service, spaced `REGISTRATION_FRAME_INTERVAL_MS` apart, picking the largest detected face in each frame.
4. The resulting embeddings are averaged and re-normalized into a single 512-dim vector.
5. The vector is stored as a new row in the `users` table (see [Data model](#data-model) below), tagged `permanent` or `temporary`.
6. Backend returns a success/error partial, swapped into the page via HTMX (no full reload).

## Request flow: recognizing someone at the door

1. The backend's recognition loop polls `/ml/latest` on a fixed interval.
2. For each detected face, it compares the embedding against all stored embeddings using cosine similarity.
3. If liveness is enabled, a passed blink check is required within its validity window before a match can be granted.
4. If the best match's score is at or above `THRESHOLD`, and (for temporary access) has not expired, access is granted: the servo opens, and the dashboard shows `Access granted: <name>`.
5. Otherwise access is denied: the door stays locked, and the dashboard shows `Access denied: Unknown`.
6. Every state transition is written to the audit log (`logs` table).

## Data model

Persistence is SQLite, accessed exclusively through `FaceDatabase` in [`MVP_v1/app/database.py`](../MVP_v1/app/database.py) — no other module touches SQL directly (see [ADR-002](architecture/adr/ADR-002-use-sqlite-through-face-database.md)). As of v2.0.0, permanent users and temporary guests share a single table:

```sql
users(
    id, name UNIQUE, embedding BLOB,   -- 512-dim float32, L2-normalized
    type CHECK(type IN ('permanent','temporary')),
    expires_at,                        -- NULL for permanent, set for temporary
    created_at
)

logs(
    id, name, score, access_type CHECK(access_type IN ('user','guest','unknown')),
    success, liveness_passed, timestamp
)

admins(
    id, username UNIQUE, password_hash, created_at   -- bcrypt hash
)
```

Full DDL: [`MVP_v1/app/schema.sql`](../MVP_v1/app/schema.sql).

## Authentication

The admin web UI uses session-cookie authentication; passwords are bcrypt-hashed, never stored or compared in plaintext (see [ADR-003](architecture/adr/ADR-003-session-auth-and-password-hashing.md)). A single admin account is bootstrapped from `.env` on first startup.

## Hardware control

The servo is accessed through a small abstraction with two interchangeable implementations (see [ADR-004](architecture/adr/ADR-004-servo-abstraction-with-emulated-mode.md)):

- **`gpio` mode** — drives a real servo via `gpiozero.AngularServo` on a configured BCM pin. Used on Raspberry Pi.
- **`emulated` mode** — mirrors the same open/close timing in software, with no hardware dependency. Used for local development and demos on any machine.

The mode is selected by `SERVO_MODE` (see [configuration.md](configuration.md)).

## Deployment topology

The product runs as two Docker Compose services:

- `backend` — the FastAPI app, port 8000, with a persistent SQLite file bind-mounted from the host (`./data:/data`).
- `ml` — the camera/ML service, port 8001 (internal), running `privileged: true` with `/dev/video0` passed through so it can access the camera.

This runs identically on a Raspberry Pi 4 (with a real camera and servo) and on an x86 laptop (with `SERVO_MODE=emulated` and any webcam), which is the primary reason SQLite and Docker Compose were chosen over a heavier database/orchestration setup for this MVP — see [ADR-002](architecture/adr/ADR-002-use-sqlite-through-face-database.md) for the tradeoffs.

For deployment steps, see [deployment-raspberry-pi.md](deployment-raspberry-pi.md) (Raspberry Pi) or [getting-started.md](getting-started.md) (local demo).

## Known limitations

- Single-host deployment — SQLite and direct device access (`/dev/video0`, GPIO) mean this does not scale horizontally.
- Single admin account bootstrapped from environment — no self-service multi-admin management yet.
- No HTTPS termination built in — put a reverse proxy in front if exposing beyond a trusted local network, and set `SESSION_COOKIE_SECURE=True`.
- LED status indicators are planned but not yet implemented; the dashboard's verdict-overlay color scheme (grey/yellow/green/red) mirrors the intended LED colors.

## Further reading

- [architecture/README.md](architecture/README.md) — component/dynamic/deployment PlantUML diagrams and a deeper coupling/cohesion/quality-requirement analysis.
- [architecture/adr/](architecture/adr/) — architecture decision records referenced above.
- [interface.md](interface.md) — detailed UI/interface contract (verdict states, screens).
