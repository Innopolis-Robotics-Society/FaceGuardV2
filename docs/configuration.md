# Configuration Reference

All runtime configuration for the backend (`MVP_v1/app/`) is read from environment variables, defined in [`MVP_v1/app/config.py`](../MVP_v1/app/config.py) and loaded from an `.env` file (or Docker Compose `env_file`). Copy [`MVP_v1/.env.example`](../MVP_v1/.env.example) to `MVP_v1/.env` and edit it — never commit the real `.env`.

This page is the authoritative list, kept in sync with `config.py`. `.env.example` documents the common ones inline; a few advanced/rarely-changed ones are only listed here.

## Recognition

| Variable | Default | Purpose |
|---|---|---|
| `THRESHOLD` | `0.45` | Cosine similarity threshold for a match. Range `0.0`–`1.0`. Higher = stricter (fewer false accepts, more false rejects). Tune with real test subjects and lighting conditions before relying on it. |
| `RECOGNITION_INTERVAL_MS` | `500` | How often the backend polls the ML service for the latest detected faces. Lower = more responsive, higher CPU/network load. |

## Registration

| Variable | Default | Purpose |
|---|---|---|
| `REGISTRATION_FRAME_COUNT` | `5` | Number of frames captured when registering a new person. The embeddings from all frames are averaged and re-normalized. |
| `REGISTRATION_FRAME_INTERVAL_MS` | `400` | Delay between consecutive registration frames. |

## Database

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_PATH` | `/data/faces.db` | Path to the SQLite file. In Docker Compose this sits under the `/data` mount point, which is bind-mounted to `./data` on the host so it survives container rebuilds. |

## ML service

| Variable | Default | Purpose |
|---|---|---|
| `ML_SERVICE_URL` | `http://ml:8001` | Base URL of the ML service (camera + face detection + embeddings). Trailing slashes are stripped automatically. In Docker Compose, `ml` resolves via the shared `faceguard` network; set this to `http://localhost:8001` if running the backend outside Docker against a Dockerized ML service. |

## Admin credentials

| Variable | Default | Purpose |
|---|---|---|
| `ADMIN_USERNAME` | `admin` | Bootstrap admin username, created on first startup if no admin exists yet. |
| `ADMIN_PASSWORD` | `change-me-on-first-login` | Bootstrap admin password (plaintext in `.env`). **Always override this before any real deployment.** |
| `ADMIN_PASSWORD_HASH` | *(unset)* | Optional pre-hashed bcrypt password. If set, it takes precedence over `ADMIN_PASSWORD`. Generate with: `python -c "import bcrypt; print(bcrypt.hashpw(b'pass', bcrypt.gensalt()).decode())"`. Preferred for deployments where you don't want the plaintext password sitting in `.env`. |

## Authentication / sessions

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `change-me-to-a-long-random-string` | Signs the session cookie. **Must** be replaced with a long random value before any real use — anyone with this value can forge admin sessions. Generate with `python -c "import secrets; print(secrets.token_hex(32))"`. |
| `SESSION_COOKIE_NAME` | `faceguard_session` | Name of the session cookie. |
| `SESSION_COOKIE_SECURE` | `False` | Set to `True` when the admin UI is served over HTTPS (e.g. behind a reverse proxy), so the cookie is only sent over encrypted connections. |

## Servo

| Variable | Default | Purpose |
|---|---|---|
| `SERVO_MODE` | `emulated` | `gpio` on a Raspberry Pi with a real servo wired up; `emulated` for local development/demo on any machine (simulates open/close timing in the UI, no hardware needed). If `gpio` mode fails to initialize (e.g. not actually running on a Pi), the backend automatically falls back to `emulated` and logs an error. |
| `SERVO_PIN` | `18` | BCM GPIO pin number for the servo signal wire. Only used in `gpio` mode. |
| `SERVO_OPEN_DURATION_SEC` | `2.0` | How long the servo stays in the open position before auto-returning to closed. Range `0.1`–`30.0`. |

## Liveness detection

| Variable | Default | Purpose |
|---|---|---|
| `LIVENESS_ENABLED` | `false` (`.env.example` ships it set to `true`) | Require a detected blink before granting access, to resist spoofing with a printed photo or a phone/tablet screen. This is the only liveness variable the backend actually acts on — see the note below. |
| `LIVENESS_EAR_THRESHOLD` | `0.20` | Eye-aspect-ratio threshold below which an eye is considered closed. Range `0.05`–`0.40`. **Not currently wired to the ML service** — see note below. |
| `LIVENESS_MIN_BLINK_DURATION_MS` | `100` | Minimum duration a detected blink must last to count as a genuine blink rather than noise. Not currently listed in `.env.example`. **Not currently wired to the ML service** — see note below. |
| `LIVENESS_TIMEOUT_SEC` | `3.0` | How long a passed liveness check remains valid before it must be re-verified. Range `1.0`–`10.0`. **Not currently wired to the ML service** — see note below. |

Liveness (blink) detection is implemented entirely in the ML service (`MVP_v1/ml_service/main.py`) using an ONNX Runtime PFLD facial-landmark model to compute eye-aspect-ratio, having replaced an earlier MediaPipe Face Mesh implementation. The ML service does not read any environment variables — its blink-sensitivity constants (EAR threshold, required blink count, liveness validity window, etc.) are hardcoded in that file. In practice this means:

- `LIVENESS_ENABLED` works as documented — it's read by the backend (`app/config.py`) and gates whether a passed blink check is required before granting access.
- `LIVENESS_EAR_THRESHOLD`, `LIVENESS_MIN_BLINK_DURATION_MS`, and `LIVENESS_TIMEOUT_SEC` are defined in `app/config.py` but currently have no effect on the actual blink-detection behavior — tuning liveness sensitivity today requires editing the constants at the top of `ml_service/main.py` (e.g. `EAR_THRESHOLD`, `REQUIRED_BLINKS`, `LIVENESS_TTL_SECONDS`) and rebuilding the `ml` image, not editing `.env`.

If you need this wired through properly, that's a real gap worth raising as a follow-up rather than something to work around via `.env`.

## Server

| Variable | Default | Purpose |
|---|---|---|
| `HOST` | `0.0.0.0` | Bind address for uvicorn. |
| `PORT` | `8000` | Bind port for uvicorn. |
| `LOG_LEVEL` | `INFO` | Backend log verbosity. |

## Display / locale

| Variable | Default | Purpose |
|---|---|---|
| `LOCAL_TIMEZONE` | `Europe/Moscow` | Timezone used to render timestamps in the admin UI and to interpret naive datetime values submitted from browser `<input type="datetime-local">` fields (e.g. guest expiry date pickers). All timestamps are stored in UTC in the database regardless of this setting. Not currently listed in `.env.example` — set it explicitly if the deployment site is in a different timezone. |

## Audit log retention

| Variable | Default | Purpose |
|---|---|---|
| `LOG_RETENTION_DAYS` | `30` | Access-log entries older than this many days are automatically deleted. Cleanup runs on backend startup and then once every 24 hours from the recognition loop. |

## Debug

| Variable | Default | Purpose |
|---|---|---|
| `ALLOW_DEBUG_SEED` | `false` | Enables a `/debug/seed-user` endpoint used for offline testing without a working ML service. **Leave this `false` in any real deployment** — it is a testing convenience, not a hardened endpoint. Not currently listed in `.env.example`. |

## Notes

- All values can be overridden either through `MVP_v1/.env` or through the environment (e.g. `docker-compose.yml`'s `env_file: .env`, or `export VAR=...` when running without Docker).
- Variable names are case-insensitive (pydantic-settings `case_sensitive=False`), but `.env.example` uses upper-case by convention — stick with that for consistency.
- Unknown/extra variables in `.env` are silently ignored (`extra="ignore"`), so a typo in a variable name will not raise an error — verify behavior after changing configuration rather than assuming it took effect.
