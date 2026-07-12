
# Customer Handover Guide

This document describes the current handover state of FaceGuardV2.

## 1. Product overview

FaceGuardV2 is a face-recognition access-control system for a laboratory door.

The product provides:

* a FastAPI backend;
* a web admin interface;
* face registration and recognition orchestration;
* SQLite-based storage for users, access data, and logs;
* camera/embedding extraction through a separate ML service;
* servo control for physical door unlocking on Raspberry Pi;
* emulated servo mode for local development;
* Docker Compose based setup for local and Raspberry Pi deployment.

The current maintained product is located in:

```text
MVP_v1/
```

The historical prototype is located in:

```text
MVP_v0/
```

`MVP_v0/` is kept for traceability only and should not be treated as the current handover version.

## 2. Current handover status

### Handover level

Current handover level:

```text
Ready for independent use
```

This means that the repository, setup instructions, runnable product version, and customer-facing documentation are prepared so that the customer can inspect and run the product using the documented steps.

### Customer confirmation status

Current customer-confirmation status:

```text
Not yet accepted
```

At the time of this document update, final Week 7 acceptance has not yet been confirmed. The product is prepared as a trial / handover-candidate version for customer review. The final confirmation status must be updated after the Week 7 transition confirmation.

### Current transition state

| Area                     | Current state                                                                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository access        | The public repository is available through the FaceGuardV2 GitHub repository.                                                                     |
| Product access           | The product can be accessed through the latest GitHub release or by running `MVP_v1/` locally with Docker Compose.                                |
| Deployment               | The product can be run locally or on Raspberry Pi using the documented setup.                                                                     |
| Customer-side operation  | Not yet confirmed.                                                                                                                                |
| Customer independent use | Not yet confirmed.                                                                                                                                |
| Ownership transfer       | Repository ownership/admin transfer to the customer is not yet completed. The repository is currently maintained by the team organization.        |
| Private credentials      | Not stored in the public repository. Private credentials must be shared only through the private submission or customer-approved private channel. |
| Final transition         | Pending Week 7 confirmation.                                                                                                                      |

## 3. Repository and ownership arrangements

The product repository is the main source of truth for the delivered course product.

Main repository entry point:

```text
../README.md
```

Current maintained implementation:

```text
../MVP_v1/
```

Current customer-facing documentation:

```text
../docs/
```

The repository is public and contains sanitized product code, documentation, reports, and public evidence. It must not contain private credentials, private access instructions, private recordings, exact private timecodes, customer-identifying information, or real biometric datasets.

### Transferred or available to the customer

The following items are available for customer or reviewer inspection:

* public repository source code;
* current maintained product implementation in `MVP_v1/`;
* setup and run instructions;
* release artifacts where published;
* public documentation in `docs/`;
* public weekly reports under `reports/`;
* changelog and release history;
* test and quality documentation.

### Intentionally retained or private

The following items are intentionally not committed to the public repository:

* real credentials;
* `.env` files with real values;
* private deployment credentials;
* private customer communication;
* private recordings;
* exact private timecodes;
* private customer acceptance evidence;
* real production face images or biometric data.

These items must be shared only through the private Moodle submission channel or another customer-approved private channel.

## 4. Product access

### Option A: Use the latest release

Use the latest GitHub release as the current product access artifact:

```text
../releases/latest
```

The release page should identify the mapped course version, link the relevant Sprint milestone, link the run or access instructions, and link this handover document.

### Option B: Run the maintained product from the repository

The maintained product is in:

```text
../MVP_v1/
```

Use the detailed setup instructions in:

```text
../MVP_v1/README.md
```

Basic local Docker Compose startup:

```bash
cd MVP_v1
cp .env.example .env
# edit SECRET_KEY, ADMIN_PASSWORD, and other required values
docker compose up --build
```

Then open:

```text
http://localhost:8000/login
```

The ML service is not intended to be used directly by the customer. The customer-facing interface is the backend web admin UI.

## 5. Normal customer use

The main customer workflow is:

1. Open the web admin interface.
2. Log in as admin.
3. Open the live dashboard.
4. Register a permanent user or temporary guest.
5. Use the camera-based recognition flow.
6. Review access logs.
7. Manage or revoke users and guests.
8. Verify that access is granted or denied correctly.
9. On Raspberry Pi, verify that successful recognition triggers the servo.

Main user-facing routes:

| Area                      | Path        |
| ------------------------- | ----------- |
| Login                     | `/login`    |
| Live dashboard            | `/`         |
| User registration         | `/register` |
| User and guest management | `/users`    |
| Access logs               | `/logs`     |
| Health check              | `/healthz`  |

Detailed user flows are documented in:

```text
../MVP_v1/README.md
```

## 6. Configuration and secrets handling

All runtime configuration for the maintained product is handled through environment variables.

Use this public example file:

```text
../MVP_v1/.env.example
```

Create a private runtime file:

```text
MVP_v1/.env
```

Do not commit `MVP_v1/.env`.

### Important configuration values

| Variable                         | Purpose                                      | Customer note                                                  |
| -------------------------------- | -------------------------------------------- | -------------------------------------------------------------- |
| `THRESHOLD`                      | Cosine similarity threshold for recognition. | Tune carefully with real test conditions.                      |
| `RECOGNITION_INTERVAL_MS`        | How often the backend polls the ML service.  | Lower values increase responsiveness but may increase load.    |
| `REGISTRATION_FRAME_COUNT`       | Number of frames captured for registration.  | Default is intended to average several embeddings.             |
| `REGISTRATION_FRAME_INTERVAL_MS` | Delay between registration frames.           | Keep stable unless camera behavior requires tuning.            |
| `DATABASE_PATH`                  | SQLite database location.                    | Should be persisted with a Docker volume in deployment.        |
| `ML_SERVICE_URL`                 | Base URL of the ML service.                  | The backend depends on this service for stream and embeddings. |
| `ADMIN_USERNAME`                 | Bootstrap admin username.                    | Use a controlled admin account.                                |
| `ADMIN_PASSWORD`                 | Bootstrap admin password.                    | Replace default value before use.                              |
| `ADMIN_PASSWORD_HASH`            | Optional pre-hashed admin password.          | Preferred for safer deployment.                                |
| `SECRET_KEY`                     | Session cookie signing key.                  | Must be replaced with a strong random secret.                  |
| `SESSION_COOKIE_SECURE`          | Secure-cookie mode.                          | Set to `True` when HTTPS is used.                              |
| `SERVO_MODE`                     | Servo mode: `gpio` or `emulated`.            | Use `gpio` on Raspberry Pi, `emulated` for local development.  |
| `SERVO_PIN`                      | BCM pin for servo signal.                    | Default documented pin is BCM 18.                              |
| `SERVO_OPEN_DURATION_SEC`        | How long the servo remains open.             | Adjust for the physical lock mechanism.                        |
| `LOG_RETENTION_DAYS`             | Audit log retention period.                  | Controls automatic cleanup of old logs.                        |

### Secrets policy

The customer must keep the following private:

* admin password;
* session `SECRET_KEY`;
* private deployment credentials;
* private network addresses if not intended for public sharing;
* any real face data or biometric data.

Only sanitized examples belong in the public repository.

## 7. Deployment instructions

### Local development or reviewer run

Use local Docker Compose:

```bash
cd MVP_v1
cp .env.example .env
docker compose up --build
```

Open:

```text
http://localhost:8000/login
```

Use `SERVO_MODE=emulated` for local development without Raspberry Pi hardware.

### Raspberry Pi deployment

For Raspberry Pi operation:

1. Install Docker on the Raspberry Pi.
2. Clone the repository.
3. Enter `MVP_v1/`.
4. Copy `.env.example` to `.env`.
5. Configure:

```ini
SERVO_MODE=gpio
SERVO_PIN=18
SERVO_OPEN_DURATION_SEC=2.0
THRESHOLD=0.45
ADMIN_PASSWORD=<private strong password>
SECRET_KEY=<private random secret>
```

6. Connect the servo according to the documented GPIO wiring.
7. Start the stack:

```bash
docker compose up -d --build
```

8. From another device on the same local network, open:

```text
http://<pi-ip>:8000/
```

9. Log in as admin and verify the live dashboard.

The Raspberry Pi deployment requires correct camera access, correct ML service configuration, and correct servo wiring. Hardware-specific issues should be checked before treating a recognition failure as a software defect.

## 8. Verification steps

After setup or deployment, verify the product with the following checklist.

### Basic availability

```bash
cd MVP_v1
docker compose ps
```

Expected result:

* backend service is running;
* ML service is running or reachable;
* web UI opens in the browser.

### Health check

Open:

```text
http://<host>:8000/healthz
```

Expected result:

* backend returns a successful health response.

### Login check

1. Open `/login`.
2. Enter configured admin credentials.
3. Confirm that the dashboard opens.

Expected result:

* login succeeds;
* session is created;
* dashboard is accessible.

### Registration check

1. Open `/register`.
2. Register a test person using sanitized test data.
3. Confirm that the user appears in `/users`.

Expected result:

* registration succeeds;
* user is saved;
* no private or real biometric data is committed to the repository.

### Recognition check

1. Open the dashboard.
2. Confirm that the camera stream is visible.
3. Present a registered test user.
4. Confirm access decision and log entry.

Expected result:

* registered user is recognized above the configured threshold;
* unknown face is denied;
* audit log records the decision.

### Servo check

For local development:

```ini
SERVO_MODE=emulated
```

Expected result:

* dashboard and logs show access behavior without physical servo movement.

For Raspberry Pi deployment:

```ini
SERVO_MODE=gpio
```

Expected result:

* successful recognition triggers the physical servo for the configured open duration.

## 9. Recovery and maintenance

### Restart the product

```bash
cd MVP_v1
docker compose restart
```

### Rebuild after code or dependency changes

```bash
cd MVP_v1
docker compose up -d --build
```

### Stop the product

```bash
cd MVP_v1
docker compose down
```

### Preserve data

The SQLite database path is configured by:

```text
DATABASE_PATH
```

For deployment, the database should be stored in a persistent Docker volume or another persistent filesystem path. Before resetting or replacing a deployment, back up the database file if registered users and logs must be preserved.

### Reset local test data

For local development only, stop the stack and remove the local development database or Docker volume according to the configured `DATABASE_PATH`.

Do not delete customer-side data unless the customer explicitly approves it.

### Update configuration

1. Stop the stack if needed.
2. Edit `MVP_v1/.env`.
3. Restart Docker Compose.
4. Run the verification checklist again.

## 10. Troubleshooting

| Problem                      | Likely cause                                                                       | Suggested action                                                                          |
| ---------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Cannot open web UI           | Backend is not running or wrong host/port.                                         | Check `docker compose ps`, `HOST`, and `PORT`.                                            |
| Login fails                  | Wrong admin credentials or changed password hash.                                  | Check private `.env` values and admin bootstrap behavior.                                 |
| Camera stream is not visible | ML service is unavailable or camera is not passed through.                         | Check `ML_SERVICE_URL`, ML service health, and `/dev/video0` passthrough on Raspberry Pi. |
| Recognition always denies    | Threshold too strict, poor lighting, bad registration sample, or ML service issue. | Re-register with better lighting and tune `THRESHOLD`.                                    |
| Recognition is unstable      | Camera angle, lighting, motion blur, or inconsistent embeddings.                   | Stabilize camera position and use multiple clean registration frames.                     |
| Servo does not move          | `SERVO_MODE` is wrong, GPIO wiring is wrong, or hardware power is insufficient.    | Verify `SERVO_MODE=gpio`, `SERVO_PIN`, wiring, and external power.                        |
| Logs grow too large          | Retention setting is too high or cleanup is not running.                           | Check `LOG_RETENTION_DAYS` and restart the service.                                       |
| Docker build fails           | Dependency, platform, or cache issue.                                              | Rebuild with clean cache and check CI or dependency files.                                |

## 11. Known limitations

The current product is a course MVP and has the following limitations:

* It is not a certified physical security system.
* Real deployment requires controlled lighting, stable camera placement, and hardware testing.
* Recognition quality depends on camera quality, registration sample quality, threshold tuning, and ML service behavior.
* Public repository examples must use sanitized data only.
* Private credentials and real deployment details are not included in public documentation.
* HTTPS termination is not provided directly by the application and should be handled by deployment infrastructure if needed.
* Multi-admin operational management is limited.
* Customer-side deployment and independent long-term operation are not yet confirmed.
* Final customer acceptance is pending Week 7 transition confirmation.

## 12. Documentation entry points

| Need                                | Document                                                     |
| ----------------------------------- | ------------------------------------------------------------ |
| Public project overview             | [../README.md](../README.md)                                 |
| Current product setup and run guide | [../MVP_v1/README.md](../MVP_v1/README.md)                   |
| Architecture documentation          | [architecture/README.md](architecture/README.md)             |
| Development process                 | [development-process.md](development-process.md)             |
| Definition of Done                  | [definition-of-done.md](definition-of-done.md)               |
| Testing documentation               | [testing.md](testing.md)                                     |
| Quality requirements                | [quality-requirements.md](quality-requirements.md)           |
| Quality requirement tests           | [quality-requirement-tests.md](quality-requirement-tests.md) |
| User acceptance tests               | [user-acceptance-tests.md](user-acceptance-tests.md)         |
| Product roadmap                     | [roadmap.md](roadmap.md)                                     |
| User stories                        | [user-stories.md](user-stories.md)                           |
| Changelog                           | [../CHANGELOG.md](../CHANGELOG.md)                           |
| Contributor guide                   | [../CONTRIBUTING.md](../CONTRIBUTING.md)                     |
| Agent guide                         | [../AGENTS.md](../AGENTS.md)                                 |

## 13. Remaining support needs

The current documentation set is sufficient for the reached handover level:

```text
Ready for independent use
```

However, the following support may still be needed before stronger handover levels can be claimed:

* customer-side trial using the Week 6 trial release;
* final customer confirmation in Week 7;
* confirmation that the customer can access and follow the setup instructions;
* customer-side Raspberry Pi deployment verification, if the customer wants hardware-side operation;
* confirmation that the customer accepts the current limitations;
* final update of this document after Week 7 feedback.

If the customer independently uses the product, deploys it, or operates it on their side, update the handover level accordingly.

## 14. Status update procedure

This document must be updated whenever any of the following changes:

* product access artifact;
* release version;
* deployment method;
* setup or run instructions;
* environment variables;
* secrets-handling expectations;
* customer feedback;
* customer acceptance status;
* handover level;
* limitations;
* troubleshooting guidance;
* support expectations.

For Week 7 final transition, update these fields at minimum:

```text
Handover level
Customer confirmation status
Current transition state
Product access
Known limitations
Remaining support needs
```

## 15. Public/private evidence separation

Public repository documents may include sanitized summaries only.

Do not publish:

* private recordings;
* exact private timecodes;
* private credentials;
* private access links;
* customer-identifying screenshots;
* private customer confirmation screenshots;
* real biometric data.

Private confirmation evidence, access credentials, customer messages, and instructor-only recordings must be placed in the Moodle PDF submission wrapper or another instructor-approved private channel.
