# FaceGuardV2

Real-time face-recognition access control system built on a Raspberry Pi
with a camera module. The system detects a face, extracts its embedding,
compares it against a database of registered users, and decides whether
to grant or deny access. On successful recognition, a servo motor rotates
to physically unlock the door.

- [Week 2 Report](reports/week2/README.md)
- [MVP v0 Report](reports/week2/mvp-v0-report.md)

---

## Project layout

| Path        | Purpose                                                       |
|-------------|---------------------------------------------------------------|
| `MVP_v0/`   | Historical prototype (Assignment 2). Standalone OpenCV script. |
| `MVP_v1/`   | **MVP v1 — FastAPI backend + Web admin (Assignment 3, Part 8).** |
| `docs/`     | Interface contract (Live Display + Web Admin).                |
| `reports/`  | Weekly reports and customer meeting artifacts.                |
| `.github/`  | PR template + Lychee link-checker workflow.                   |

---

## Quick start

### MVP v0 — Windows standalone (legacy)

1. Go to **[GitHub Releases](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/)**.
2. Download the latest `FaceVerification.zip` from the Assets section.
3. Unzip it, run `FaceVerification.exe`.

> Built with PyInstaller. Runs only on Windows in this release.

### MVP v1 — Backend + Web admin (current development)

See [`MVP_v1/README.md`](MVP_v1/README.md) for the full guide.

**TL;DR (local dev with the ML stub):**

```bash
cd MVP_v1
cp .env.example .env
# edit SECRET_KEY and ADMIN_PASSWORD
docker compose up --build
# open http://localhost:8000/login
```

**On Raspberry Pi 4 (production):**

1. Set `SERVO_MODE=gpio`, `SERVO_PIN=18` in `MVP_v1/.env`.
2. Wire the servo (signal → BCM 18, VCC → 5V, GND → GND).
3. Replace the `ml:` service in `MVP_v1/docker-compose.yml` with your
   team's real ML image (and uncomment `/dev/video0` device passthrough).
4. `docker compose up -d --build`.
5. From any device on the same LAN, open `http://<pi-ip>:8000/`.

---

## License

[MIT](LICENSE)
