# Getting Started

This page gets FaceGuardV2 running as quickly as possible so you can see it work before doing a full hardware deployment. There are two paths:

- **Local demo** (this page) — runs on any laptop with Docker, no camera hardware or servo required. The door lock is simulated on screen.
- **Raspberry Pi deployment** — the real, hardware-connected setup with a physical camera and servo lock. See [deployment-raspberry-pi.md](deployment-raspberry-pi.md).

## Prerequisites

- Docker and Docker Compose ([get.docker.com](https://get.docker.com) or Docker Desktop).
- A webcam (built-in laptop camera works) if you want to test live recognition, not just log in.
- Git, to clone the repository.

## 1. Clone and configure

```bash
git clone https://github.com/Innopolis-Robotics-Society/FaceGuardV2.git
cd FaceGuardV2/MVP_v1
cp .env.example .env
```

Open `.env` and set at least:

```ini
SECRET_KEY=<any random string for local testing>
ADMIN_PASSWORD=<a password you'll remember>
SERVO_MODE=emulated
```

`SERVO_MODE=emulated` is the default — it shows the door "opening" and "closing" in the UI instead of driving real hardware, so this works on any laptop.

## 2. Start the stack

```bash
docker compose up --build
```

This starts two services:

- **backend** (`http://localhost:8000`) — the web admin UI you'll actually use.
- **ml** (`http://localhost:8001`) — the camera/face-recognition service. It is not meant to be opened directly in a browser.

The first run downloads and prepares the face-recognition model, so it takes a few minutes. Subsequent runs are fast.

## 3. Log in

Open:

```text
http://localhost:8000/login
```

Log in with `ADMIN_USERNAME` (default `admin`) and the `ADMIN_PASSWORD` you set in `.env`.

## 4. Try the golden path

1. Go to the dashboard (`/`) — you should see your webcam feed with a `Waiting for face...` overlay.
2. Go to `/register`, fill in a name, choose **Permanent**, and click **Capture & register**. Look at the camera while it captures 5 frames.
3. Go back to the dashboard (`/`) — looking at the camera again should show `Access granted: <your name>` and the simulated servo will show as "triggered" for a couple of seconds.
4. Have someone else (or step out of frame and use a photo) show their face — it should show `Access denied: Unknown`.
5. Check `/logs` — both attempts should be recorded.

## 5. Next steps

- Deploying to real hardware: [deployment-raspberry-pi.md](deployment-raspberry-pi.md).
- Understanding what each environment variable does: [configuration.md](configuration.md).
- Full walkthrough of every admin UI screen: [user-guide.md](user-guide.md).
- How the system is put together: [architecture.md](architecture.md).
- Something not working as expected: [troubleshooting.md](troubleshooting.md).

## Stopping the demo

```bash
docker compose down
```

Your registered users and logs are kept in `MVP_v1/data/faces.db` and will still be there next time you run `docker compose up`. Delete that file (with the stack stopped) if you want to start from a clean database.
