# Troubleshooting

Common problems when running or deploying FaceGuardV2, and what to check first.

## Can't open the web UI

- Check both containers are actually up: `docker compose ps` (run from `MVP_v1/`). Both `backend` and `ml` should show `running`.
- Confirm you're using the right host/port — default is `http://<host>:8000/login`, not 8001 (that's the internal ML service).
- Check `HOST`/`PORT` in `.env` haven't been changed away from `0.0.0.0`/`8000`.
- On Raspberry Pi, confirm you're using the Pi's LAN IP, not `localhost`, when connecting from another device.

## Login fails

- Confirm you're using the current `ADMIN_USERNAME`/`ADMIN_PASSWORD` from `.env`. These are only used to bootstrap the admin account on first startup — if the account already existed with a different password, editing `.env` afterwards won't change it.
- If you set `ADMIN_PASSWORD_HASH`, it takes precedence over `ADMIN_PASSWORD` — make sure only one is set to what you expect.
- Check `SECRET_KEY` hasn't changed since the session cookie was issued (changing it invalidates all existing sessions — log in again).

## Camera stream is not visible

- Check the ML service is reachable: `ML_SERVICE_URL` should point to `http://ml:8001` inside Docker Compose (or `http://localhost:8001` if running the backend outside Docker against a Dockerized ML service).
- Check `/dev/video0` exists on the host: `ls /dev/video0`. If the camera enumerates under a different device number, either fix the enumeration order or update the `devices:` line in `MVP_v1/docker-compose.yml`.
- Confirm the `ml` service has `privileged: true` and the device mapping in `docker-compose.yml` — both are required for camera access in the container.
- Check the `ml` container logs: `docker compose logs ml`.

## Recognition always denies / never matches

- `THRESHOLD` may be too strict for your camera/lighting — see [configuration.md](configuration.md). Lower it slightly and re-test; don't lower it so far that unrelated faces start matching.
- Poor lighting or an off-angle registration sample produces a weak embedding. Re-register the person with even, front-facing lighting.
- Confirm the ML service is actually running and healthy (dashboard status panel, or `GET /health` on port 8001) — if it's down, recognition can't happen at all and you'd expect a `System error` state rather than a plain denial.

## Recognition is unstable (flickers between granted/denied)

- Usually camera angle, motion blur, or inconsistent lighting. Stabilize the camera mount and avoid backlighting.
- Re-register with a few different natural head angles rather than a single very-close frontal shot.

## Servo does not move (Raspberry Pi)

- Confirm `SERVO_MODE=gpio` in `.env` — if it's still `emulated`, no physical hardware is driven.
- Check the wiring against [deployment-raspberry-pi.md](deployment-raspberry-pi.md#2-wire-the-servo): signal → BCM 18 (pin 12) by default, VCC → 5V, GND → GND.
- If the servo twitches or the Pi seems to brown out/reboot when the door opens, the Pi's own 5V rail likely can't supply enough current — move the servo's VCC to an external 5V supply with a shared ground.
- Check `SERVO_PIN` matches how you actually wired it.
- If GPIO initialization fails for any reason, the backend automatically falls back to `emulated` mode and logs an error — check `docker compose logs backend` for a message like "Failed to init GpioServo".

## Servo doesn't move in local/demo setup

- Expected — `SERVO_MODE=emulated` (the default for non-Pi setups) only shows the "triggered" state in the dashboard status panel; there is no real hardware to move.

## Liveness / blink check seems to block valid users

- Confirm you're actually blinking naturally while looking at the camera — the check requires a detected blink within `LIVENESS_TIMEOUT_SEC`.
- If it's consistently too strict, review `LIVENESS_EAR_THRESHOLD` in [configuration.md](configuration.md) — lowering it makes blink detection more permissive, but a value that's too low increases the risk of false-positive "blinks."
- To rule it out while debugging something else, temporarily set `LIVENESS_ENABLED=false`, restart, and re-test.

## Logs grow too large / old entries aren't cleaned up

- Check `LOG_RETENTION_DAYS` — cleanup runs on startup and then once every 24 hours. If the backend has been restarting frequently or has been down for a long stretch, the next cleanup may be overdue; restarting the backend triggers an immediate cleanup pass.

## Docker build fails

- Rebuild with a clean cache: `docker compose build --no-cache`.
- Check available disk space and memory — the `ml` image bakes in an InsightFace model at build time, which is memory/CPU-intensive on a Raspberry Pi's first build.
- Check `docker compose logs` for the specific dependency or platform error, and compare against the CI build (`.github/workflows/ci.yml`) which builds the same `backend` image on `amd64` — note CI does **not** build or test the `ml` image or an `arm64` target, so an ARM-specific build failure will not show up there.

## Database / data loss concerns

- The SQLite file lives at `DATABASE_PATH` (default `/data/faces.db`), bind-mounted to `MVP_v1/data/` on the host via `docker-compose.yml`. Deleting that directory deletes all registered users, guests, and audit history — back it up before any destructive operation.
- `docker compose down` does **not** delete the bind-mounted data directory; only removing `MVP_v1/data/` on the host does.

## Still stuck?

Check the container logs for both services:

```bash
cd MVP_v1
docker compose logs backend
docker compose logs ml
```

and confirm your `.env` matches the reference in [configuration.md](configuration.md).
