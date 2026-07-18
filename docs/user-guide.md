# User Guide — Admin Web UI

This guide walks through every screen of the FaceGuardV2 admin interface. It assumes the system is already running — see [getting-started.md](getting-started.md) or [deployment-raspberry-pi.md](deployment-raspberry-pi.md) if not.

The admin UI is reachable from any device on the same network as the backend, at `http://<host>:8000/`. It requires login; there is no public/unauthenticated view.

## Logging in

Open `/login` and enter the admin username/password configured via `ADMIN_USERNAME`/`ADMIN_PASSWORD` (or `ADMIN_PASSWORD_HASH`) in `.env`. The session lasts 12 hours, after which you'll need to log in again.

## Dashboard (`/`)

The dashboard is the main screen, showing:

- **Live camera feed**, with a colored verdict overlay reflecting the recognition loop's current state:

  | State | Overlay | Meaning |
  |---|---|---|
  | Idle | Grey — `Waiting for face...` | No face currently detected. Door locked. |
  | Liveness check | Yellow — `Liveness check: please blink` | A match was found; waiting for a blink before granting access (only when liveness is enabled). |
  | Granted | Green — `Access granted: <Name>` | Match found above threshold (and liveness passed, if enabled). Door unlocks. |
  | Denied | Red — `Access denied` | Face detected but no match above threshold. Door stays locked. |

- **Status panel**, showing: ML service health (online/offline), door state, last recognized user and score, counts of permanent users/active guests/log entries, and current servo state.

  The "Door" and "Servo" fields both react to the same verdict but show different things: "Door" reflects the access decision (`Locked` in grey/yellow/red depending on why, or `Opened` in green), while "Servo" only reflects the physical actuator (`Idle` or `Triggered`) and is not colour-coded — see [interface.md, §1](interface.md#1-live-display-web) for the full state-by-state breakdown across the camera overlay, door status, and servo status.

Updates arrive live over Server-Sent Events — the page does not need to be refreshed.

## Registering a person (`/register`)

1. The live camera preview appears in the left panel.
2. Fill in:
   - **Full name** — must be unique among current users/guests.
   - **Access type** — `Permanent` (never expires) or `Temporary` (an additional **Valid for (days)** field appears).
3. Click **Capture & register**. The system captures several frames (default 5) over about two seconds, takes the largest face in each frame, and averages the embeddings.
4. A success or error message appears in place — no page reload.

Common failure messages and what they mean:

| Message | Cause |
|---|---|
| `User '<name>' already exists.` | The name is already registered. Use a different name, or edit/delete the existing entry first. |
| `No face detected on frame N/5.` | The person moved out of frame, lighting was too poor, or they were too far/close during capture. Try again with better lighting and a steady position. |
| `ML service error on frame N: ...` | The ML service is unreachable or errored. Check its container/logs. |

## Users & guests (`/users`)

Lists every permanent user and every currently active (non-expired) guest, with:

- Delete (permanent users) / Revoke (guests) buttons for immediate removal.
- A **Purge expired** button to force-clean expired guests immediately (they are also purged automatically during recognition, so this is mainly useful right after an expiry to tidy the list).
- Clicking a name opens its detail page, `/users/{id}`, showing full metadata (type, expiration if temporary, creation date), an edit form (name, access type, expiration date — the expiration field appears/disappears automatically based on the selected type), a delete ("danger zone") action, and that person's last 50 audit-log entries.

## Access logs (`/logs`)

Lists the most recent access attempts (up to 300), each with timestamp, matched name (or `Unknown`), access type (`user`/`guest`/`unknown`), similarity score, and whether access was granted. Filter by name substring and/or restrict to today only.

A JSON version is available at `/api/logs` for scripting/integration purposes.

## Programmatic access (JSON API)

For integration or bulk management, the backend also exposes a JSON CRUD API under `/backend/users`, requiring the same session authentication as the web UI:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/backend/users` | List users, with optional `?type=` and `?include_expired=` filters. |
| `GET` | `/backend/users/{id}` | Get one user. |
| `PUT` | `/backend/users/{id}` | Update name/type/expiration/embedding. Switching to `temporary` requires an `expires_at` (unless one is already set in the future). Duplicate name returns 409. |
| `DELETE` | `/backend/users/{id}` | Delete a user. |

## Liveness detection

If `LIVENESS_ENABLED=true` (see [configuration.md](configuration.md)), the ML service requires a detected blink (via eye-aspect-ratio analysis) before a face can be granted access, to resist someone holding up a photo or a screen showing a photo. This adds a brief natural pause before access is granted — present your face normally and blink as you would anyway; no special action is needed.

## Health check

`GET /healthz` returns a simple health response and requires no authentication — useful for monitoring or for confirming the backend is reachable at all (see [deployment-raspberry-pi.md](deployment-raspberry-pi.md) verification checklist).
