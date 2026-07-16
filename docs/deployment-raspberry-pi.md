# Deploying on Raspberry Pi 4

This guide walks through installing FaceGuardV2 on a physical Raspberry Pi 4, wiring the servo lock, and verifying the deployment. It assumes you already have a Raspberry Pi 4 running Raspberry Pi OS (64-bit recommended) with network access.

For a quick local demo without any hardware, see [getting-started.md](getting-started.md) instead. For what each configuration value does, see [configuration.md](configuration.md).

## 1. Hardware requirements

| Item | Notes |
|---|---|
| Raspberry Pi 4 (2 GB RAM or more) | Raspberry Pi OS, 64-bit recommended. |
| Compatible camera | USB webcam or Raspberry Pi Camera Module exposed as `/dev/video0`. |
| SG90-class servo | Or an equivalent small hobby servo used to actuate the door latch. |
| microSD card, 16 GB+ | For the OS and Docker images. |
| **External 5V power supply for the servo** | Recommended. Powering the servo from the Pi's own 5V rail works for light loads, but can brown out the Pi under load — see [servo.py](../MVP_v1/app/servo.py) comments. If you see the Pi rebooting or the camera dropping out when the door unlocks, move the servo's VCC to a separate 5V supply with a shared ground. |

## 2. Wire the servo

| Servo wire | Raspberry Pi pin |
|---|---|
| Signal | BCM 18 (physical pin 12) |
| VCC (red) | 5V (physical pin 2 or 4), or external 5V supply |
| GND (brown/black) | GND (physical pin 6) |

The signal pin is configurable via `SERVO_PIN` (default `18`, BCM numbering) if you need to wire it elsewhere.

Connect the camera (USB webcam, or Pi Camera Module via a CSI-to-USB/V4L2 adapter) so it is visible as `/dev/video0`. Check with:

```bash
ls /dev/video0
```

If you have multiple cameras and it isn't `/dev/video0`, either re-order the devices or edit the `devices:` mapping in `MVP_v1/docker-compose.yml`.

## 3. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# log out and back in for the group change to take effect
```

Verify:

```bash
docker --version
docker compose version
```

## 4. Get the code onto the Pi

```bash
git clone https://github.com/Innopolis-Robotics-Society/FaceGuardV2.git
cd FaceGuardV2/MVP_v1
```

## 5. Configure the environment

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```ini
SERVO_MODE=gpio
SERVO_PIN=18
SERVO_OPEN_DURATION_SEC=2.0

ADMIN_USERNAME=admin
ADMIN_PASSWORD=<a strong password — do not leave the default>
SECRET_KEY=<a random 32+ byte secret>

THRESHOLD=0.45
```

Generate a random `SECRET_KEY`:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

See [configuration.md](configuration.md) for the full list of variables, including recognition threshold tuning, liveness detection, and log retention. Never commit the real `.env` file — it stays local to the Pi.

## 6. Start the stack

```bash
docker compose up -d --build
```

This builds and starts two containers:

- `backend` — the web admin UI and recognition/decision logic, on port `8000`.
- `ml` — the camera-owning face-detection/embedding service, on port `8001` (internal, not meant to be opened directly). It runs with `privileged: true` and `/dev/video0` passed through so it can access the camera.

The first build downloads and bakes two models into the `ml` image: the InsightFace face-recognition model, and a PFLD facial-landmark model (used for liveness/blink detection), so the first `docker compose up --build` takes noticeably longer than later runs and **requires network access on the build machine**.

If the PFLD model download fails during the build (no network, or the source URL is unreachable), the build currently continues anyway with just a warning printed — it does not fail. In that case the `ml` container will build successfully but crash on startup with a `FileNotFoundError` for `pfld.onnx`. If the `ml` service won't start after a fresh build, check `docker compose logs ml` for this before assuming it's a camera or GPIO problem.

## 7. Open the admin UI

From another device on the same local network:

```text
http://<pi-ip>:8000/login
```

Log in with the admin credentials you set in `.env`.

## 8. Verify the deployment

Work through this checklist before considering the deployment done:

| Check | How | Expected result |
|---|---|---|
| Containers are up | `docker compose ps` | Both `backend` and `ml` show `running`. |
| Backend is healthy | Open `http://<pi-ip>:8000/healthz` | Returns a successful health response. |
| Camera stream works | Open the dashboard at `/` | Live camera feed is visible with a verdict overlay (`Waiting for face...` when idle). |
| Login works | `/login` with your admin credentials | Session is created, dashboard loads. |
| Registration works | Register a test person at `/register` | Person appears in `/users`. |
| Recognition works | Present the registered person to the camera | Overlay shows `Access granted: <name>`, an entry appears in `/logs`. |
| Unknown face is denied | Present an unregistered face | Overlay shows `Access denied: Unknown`, door stays locked. |
| Servo actuates | Successful recognition | Servo physically rotates open for `SERVO_OPEN_DURATION_SEC` seconds, then returns to closed. |

If any step fails, see [troubleshooting.md](troubleshooting.md).

## 9. Data persistence

The SQLite database (users, guests, admin account, audit logs) lives at `/data/faces.db` inside the `backend` container, which is bind-mounted to `MVP_v1/data/` on the Pi's filesystem (`./data:/data` in `docker-compose.yml`). This means the database survives `docker compose up -d --build` (rebuilds/restarts) but will not exist until the stack is started at least once.

Back up `MVP_v1/data/faces.db` (and its `-wal`/`-shm` companion files, if present) before any operation that could remove that directory.

## 10. Day-to-day operations

Restart the stack:

```bash
cd MVP_v1
docker compose restart
```

Rebuild after pulling new code or changing dependencies:

```bash
cd MVP_v1
git pull
docker compose up -d --build
```

Stop the stack:

```bash
cd MVP_v1
docker compose down
```

Apply a configuration change:

```bash
# edit MVP_v1/.env
docker compose restart
```

## 11. Security notes for a real deployment

- Replace `ADMIN_PASSWORD` and `SECRET_KEY` before exposing the Pi to anyone beyond yourself.
- The application does not terminate HTTPS itself. If the Pi is reachable beyond a trusted local network, put it behind a reverse proxy that terminates TLS, and set `SESSION_COOKIE_SECURE=True`.
- Only one admin account is bootstrapped from `.env`. Additional admin accounts currently require direct use of `FaceDatabase.add_admin()` — there is no self-service admin invite flow yet.
