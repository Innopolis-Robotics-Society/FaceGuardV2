# FaceGuard — Interface Documentation

## Overview

FaceGuard exposes two interfaces. As of MVP v1, the **Web Admin UI** replaces
the CLI design documented in earlier sprints.

| Interface     | Type        | User             | Status in MVP v1        |
|---------------|-------------|------------------|-------------------------|
| **Live Display**  | Web (MJPEG + SSE) | Employees, guests   | Implemented             |
| **Admin Web UI**  | Web (HTML + HTMX) | System administrators | Implemented (MVP v1)    |
| ~~Admin CLI~~     | ~~CLI~~           | ~~Administrators~~  | **Replaced by Web Admin** |

The CLI design (`register`, `remove`, `list`, `add-guest`, `logs`, `status`,
`threshold`) has been superseded by the web admin — every CLI action now
has an equivalent page (see mapping table below).

---

## 1. Live Display (Web)

The live camera feed and verdict overlay shown to anyone standing in front
of the door. The same MJPEG stream is also embedded in the admin dashboard
so the admin can see what the camera sees from their laptop.

**URL (admin view):** `/` (dashboard, requires login)

### States

A single recognition **verdict** (`idle` / `liveness_check` / `granted` /
`denied`) drives three separate visual indicators on the dashboard at
once: the camera overlay text, the "Door" status field, and the "Servo"
status field. They read the same event but don't carry the same level of
detail — the tables below give the exact text/colour for each, side by
side, since that's easy to lose track of when reading the three UI
elements separately.

> Note: a `scanning` CSS class and colour also exist in the stylesheet
> from an earlier design, but the recognition loop never actually emits
> a `scanning` verdict — the transition state users actually see is
> `liveness_check`. Treat `scanning` as dead styling, not a real state.

#### 1.1 Camera overlay (text shown on the video feed)

| Verdict | Overlay text | Meta line | Colour |
|---|---|---|---|
| `idle` | `Waiting for face...` | — | Grey |
| `liveness_check` | `Liveness check: please blink` | `{name} · score {score:.3f}` | Yellow |
| `granted` | `Access granted: {Name}` | `{access_type} · score {score:.3f}` | Green |
| `denied` | `Access denied` | `score {score:.3f}` | Red |

#### 1.2 Door status (dashboard status panel, "Door" row)

| Verdict | Text | Colour |
|---|---|---|
| `idle` | `Locked` | Grey |
| `liveness_check` | `Locked` | Yellow |
| `denied` | `Locked` | Red |
| `granted` | `Opened` | Green |

#### 1.3 Servo status (dashboard status panel, "Servo" row)

| Verdict | Text | Colour |
|---|---|---|
| `idle`, `denied`, `liveness_check` | `Idle` | Grey |
| `granted` | `Triggered` | Grey — **unchanged from `Idle`; the servo field carries no colour coding at all today**, unlike the door status and camera overlay above. |

The servo field only ever reports the mechanical actuator's own state
(idle vs. actuated) rather than the semantic access decision, which is
why it doesn't need the same colour split as the door status and camera
overlay — those two describe *why* the door is locked or open, while the
servo field describes *what the motor is physically doing*.

### Mockups

```
┌─────────────────────┐        ┌─────────────────────┐
│  [Camera feed]      │        │  [Camera feed]      │
│                     │        │   ┌─────────┐       │
│                     │        │   │  face   │       │
└─────────────────────┘        │   └─────────┘       │
   Waiting for face...         │  Access granted:    │
        (grey)                 │  Ivanov Petr        │
                                │  user · 0.821       │
                                └─────────────────────┘
                                        (green)

┌─────────────────────┐        ┌─────────────────────┐
│  [Camera feed]      │        │  [Camera feed]      │
│   ┌─────────┐       │        │   ┌─────────┐       │
│   │  face   │       │        │   │  face   │       │
│   └─────────┘       │        │   └─────────┘       │
│  Liveness check:    │        │  Access denied      │
│  please blink       │        │  score 0.312        │
└─────────────────────┘        └─────────────────────┘
        (yellow)                       (red)
```

---

## 2. Admin Web UI

Accessible from any device on the same LAN as the Raspberry Pi.
**URL:** `http://<pi-ip>:8000/`

### 2.1 Authentication

- Login form at `/login`.
- Single admin account bootstrapped from env on first startup
  (`ADMIN_USERNAME` / `ADMIN_PASSWORD`).
- Password stored bcrypt-hashed in SQLite (`admins` table).
- Session cookie (`faceguard_session`), 12h expiry.

### 2.2 Dashboard — `/`

- Live camera feed (MJPEG from ML service, proxied through backend).
- Verdict overlay (see Live Display section above).
- Status panel:
  - ML service health (online / offline)
  - Door state (locked / open)
  - Last recognized user + score
  - Counts: permanent users, active guests, total log entries
  - Servo state
- Updates pushed via SSE (`/status/events`) — no polling.

### 2.3 Users & Guests — `/users`

Lists permanent users and active (non-expired) guests with delete/revoke
buttons. Each row shows ID, name, and either `created_at` (users) or
`expires_at` (guests).

Expired guests are auto-purged inside the recognition loop — no manual
cleanup needed, but a `Purge expired` button is available for forced cleanup.

### 2.4 Register a new person — `/register`

The admin-side counterpart of US-02.

**Steps:**

1. The page shows a live camera preview (left panel).
2. Admin fills the form:
   - **Full name** (`Surname Firstname`) — unique among permanent users.
   - **Access type**:
     - `Permanent` — never expires.
     - `Temporary` — additional field `Valid for (days)` appears (HTMX swap).
3. Admin clicks **Capture & register**.
4. The backend captures `REGISTRATION_FRAME_COUNT` (default 5) frames from
   the ML service at `REGISTRATION_FRAME_INTERVAL_MS` intervals. For each
   frame the biggest detected face's embedding is taken.
5. The 5 embeddings are averaged and L2-normalized.
6. The result is saved as a `users` row (permanent) or a `guests` row
   (temporary, with `expires_at = now + N days`).
7. A success/error message is swapped in via HTMX — no page reload.

**Failure modes shown to the admin:**

- Name already exists → `User '<name>' already exists.`
- No face in one of the frames → `No face detected on frame N/5.`
- ML service unreachable → `ML service error on frame N: ...`

### 2.5 Logs — `/logs`

Audit log (US-10). Each row records:

| Field        | Source                          |
|--------------|---------------------------------|
| timestamp    | when the attempt happened       |
| name         | matched name, or `Unknown`      |
| access_type  | `user` / `guest` / `unknown`    |
| score        | cosine similarity, `0..1`       |
| success      | `true` if access was granted    |

Filters:

- **Filter by name** — substring match (e.g. `Ivan` matches `Ivanov`).
- **Today only** — restrict to today's attempts.

### 2.6 Settings — runtime threshold (US-08)

The recognition threshold is read from env at startup (`THRESHOLD`).
A runtime-adjustable threshold UI is planned for v2; for MVP v1 the
threshold is configured via `.env` / Docker env.

---

## 3. CLI → Web admin mapping

The CLI commands documented in earlier sprints have the following web
equivalents in MVP v1:

| Old CLI command              | Web admin equivalent                          |
|------------------------------|-----------------------------------------------|
| `register <name>`            | `/register` form (permanent access)           |
| `add-guest <name> --hours N` | `/register` form (temporary access, days)     |
| `remove <name>`              | Delete button on `/users`                     |
| `list`                       | `/users` page                                 |
| `logs [--today] [--user X]`  | `/logs` page (same filters)                   |
| `status`                     | Dashboard right panel (`/`)                   |
| `threshold <value>`          | `.env: THRESHOLD` (runtime UI planned v2)     |

---

## 4. Interface comparison

| Aspect            | Live Display              | Admin Web UI                  |
|-------------------|---------------------------|-------------------------------|
| User              | Employee, guest           | System admin                  |
| Input             | None (passive)            | Forms, buttons (HTMX)         |
| Output            | MJPEG + verdict overlay   | HTML pages, SSE updates       |
| Location          | Pi + camera               | Any LAN device, browser       |
| Authentication    | Biometric (face)          | Username + password (session) |
| Latency           | Real-time (≤ 500ms tick)  | On-demand                     |
| MVP v1            | ✓                          | ✓                             |

---

## 5. Hardware feedback (servo + LED)

### Servo (US-06 / US-07)

- On **Raspberry Pi** (`SERVO_MODE=gpio`): backend drives the servo via
  `gpiozero.AngularServo` on `SERVO_PIN`. On access granted, the servo
  rotates to 90° for `SERVO_OPEN_DURATION_SEC`, then returns to 0°.
- On **x86 laptops** (`SERVO_MODE=emulated`): no hardware. The status panel
  on the dashboard shows `Servo: Triggered (open)` for the same duration,
  replicating the timing of the physical actuator.

### LED indicators

Customer-requested physical LED feedback (green=granted, red=denied,
yellow=liveness check in progress, all off=idle) is implemented in
`app/leds.py` and driven from the same verdict value already used for the
door status and camera overlay in [§1](#1-live-display-web) — so the
physical LEDs and the on-screen overlay always agree. `gpio` mode drives
real LEDs via `gpiozero.LED` on Raspberry Pi; `emulated` mode logs the
state change instead (used for local development). Selected by `LED_MODE`;
pins and grant-LED duration are configurable — see
[configuration.md](configuration.md).

---

## 6. API summary

All admin endpoints require a valid session cookie (except `/login` and `/healthz`).

| Method | Path                         | Auth | Purpose                          |
|--------|------------------------------|------|-----------------------------------|
| GET    | `/login`                     | —    | Login form                       |
| POST   | `/login`                     | —    | Submit credentials               |
| POST   | `/logout`                    | ✓    | End session                      |
| GET    | `/`                          | ✓    | Live dashboard                   |
| GET    | `/users`                     | ✓    | Users + guests list              |
| GET    | `/users/{id}`                | ✓    | User detail + edit page          |
| POST   | `/users/{id}/update`         | ✓    | Update user from detail page     |
| POST   | `/users/{id}/delete`         | ✓    | Delete permanent user            |
| POST   | `/guests/{id}/delete`        | ✓    | Revoke guest                     |
| POST   | `/guests/purge`              | ✓    | Force-purge expired guests       |
| GET    | `/register`                  | ✓    | Registration form                |
| POST   | `/register`                  | ✓    | Capture frames → save            |
| GET    | `/register/options/{kind}`   | ✓    | HTMX partial for access-type     |
| GET    | `/logs`                      | ✓    | HTML audit log                   |
| GET    | `/api/logs`                  | ✓    | JSON audit log                   |
| GET    | `/stream`                    | ✓    | MJPEG camera stream               |
| GET    | `/status/events`             | ✓    | SSE verdict stream               |
| GET    | `/status/snapshot`           | ✓    | One-shot status JSON              |
| GET    | `/healthz`                   | —    | Health probe                      |
| GET    | `/backend/users`             | ✓    | JSON list, with `type`/`include_expired` filters |
| GET    | `/backend/users/{id}`        | ✓    | JSON get one user                |
| PUT    | `/backend/users/{id}`        | ✓    | JSON update user                 |
| DELETE | `/backend/users/{id}`        | ✓    | JSON delete user                 |

See [user-guide.md](user-guide.md) for what each screen does, and [MVP_v1/README.md](../MVP_v1/README.md) for the ML-service-facing internal API contract.
