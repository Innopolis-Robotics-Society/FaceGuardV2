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

The verdict overlay reflects the current state of the recognition loop.

#### 1.1 Idle (no face detected)

- **Overlay colour:** grey
- **Text:** `Waiting for face...`
- Door stays locked, servo idle.

```
┌─────────────────────┐
│  [Camera feed]      │
│                     │
│                     │
└─────────────────────┘
   Waiting for face...
        (grey)
```

#### 1.2 Scanning (face detected, comparison in flight)

- **Overlay colour:** yellow
- **Text:** `Scanning...`
- Brief — lasts one recognition tick (≤ `RECOGNITION_INTERVAL_MS`).

#### 1.3 Granted (known user / guest)

- **Overlay colour:** green
- **Text:** `Access granted: {Name}`
- **Meta:** `{access_type} · score {score:.3f}`
- Door status flips to "Open".
- Servo rotates to the open position for `SERVO_OPEN_DURATION_SEC`, then
  returns. On x86 (no GPIO), the servo state is reflected in the status
  panel as "Triggered (open)".

```
┌─────────────────────┐
│  [Camera feed]      │
│   ┌─────────┐       │
│   │  face   │       │
│   └─────────┘       │
│  Access granted:    │
│  Ivanov Petr        │
│  user · 0.821       │
└─────────────────────┘
        (green)
```

#### 1.4 Denied (face seen but no match above threshold)

- **Overlay colour:** red
- **Text:** `Access denied: Unknown`
- **Meta:** `score {best:.3f}`
- Door stays locked. Audit log entry written (`success=false`).

```
┌─────────────────────┐
│  [Camera feed]      │
│   ┌─────────┐       │
│   │  face   │       │
│   └─────────┘       │
│  Access denied:     │
│  Unknown            │
│  score 0.312        │
└─────────────────────┘
        (red)
```

#### 1.5 Error (ML service unreachable / loop crashed)

- **Overlay colour:** dark red
- **Text:** `System error`
- **Meta:** short diagnostic (e.g. `ML service unreachable`)
- Status panel shows `ML service: Offline`.

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

### LED indicators (planned for v2)

Customer-requested LED feedback (green=granted, red=denied, yellow=scanning)
is documented but not yet wired in MVP v1. The verdict overlay colour
scheme mirrors the planned LED colours so the visual feedback contract is
already stable.

---

## 6. API summary

All admin endpoints require a valid session cookie. See `README.md` for
the full HTTP method / path table.
