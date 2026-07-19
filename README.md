# FaceGuardV2

FaceGuardV2 is a face-recognition access-control system for a laboratory door. It runs as a FastAPI web admin application with a separate ML service for camera-based face detection, embedding extraction, and liveness (blink) checking, SQLite persistence, audit logging, and servo-door control on Raspberry Pi 4 or emulated hardware.

## Current product access

* **Current product release:** [Latest GitHub Release](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/latest)
* **Full documentation site:** [FaceGuardV2 Docs](https://b3ss0n.github.io/FaceGuardV2DocsWebsite/)
* **Get started:** [docs/getting-started.md](docs/getting-started.md)
* **Deploy on Raspberry Pi:** [docs/deployment-raspberry-pi.md](docs/deployment-raspberry-pi.md)
* **Handover status and support scope:** [docs/customer-handover.md](docs/customer-handover.md)

## Product status

FaceGuardV2 is a customer-usable access-control prototype providing:

* admin login and protected web interface;
* live camera stream through the backend;
* permanent user and temporary guest registration;
* face-recognition decision flow using stored embeddings, with optional liveness (blink) checking;
* access audit logging;
* user and guest management (web UI + JSON API);
* servo actuation and LED status indicators (granted / denied / liveness-pending) in GPIO mode on Raspberry Pi 4, or emulated mode for local development;
* Docker Compose based local and Raspberry Pi deployment.

Historical prototype code is kept in `MVP_v0/`. The maintained backend and web admin product lives in `MVP_v1/`.

## Quick start

```bash
cd MVP_v1
cp .env.example .env
# edit SECRET_KEY, ADMIN_PASSWORD, and other environment values
docker compose up --build
```

Then open `http://localhost:8000/login`. See [docs/getting-started.md](docs/getting-started.md) for the full first-run walkthrough, and [docs/deployment-raspberry-pi.md](docs/deployment-raspberry-pi.md) for deploying to real hardware.

## Documentation

### Using and deploying the product

| Need | Document |
| --- | --- |
| Browse all documentation in one place | [Hosted documentation site](https://b3ss0n.github.io/FaceGuardV2DocsWebsite/) |
| Quick local demo | [docs/getting-started.md](docs/getting-started.md) |
| Raspberry Pi 4 deployment | [docs/deployment-raspberry-pi.md](docs/deployment-raspberry-pi.md) |
| How the system is put together | [docs/architecture.md](docs/architecture.md) |
| Environment variables | [docs/configuration.md](docs/configuration.md) |
| Using the admin UI | [docs/user-guide.md](docs/user-guide.md) |
| Interface / UI contract details | [docs/interface.md](docs/interface.md) |
| Fixing a problem | [docs/troubleshooting.md](docs/troubleshooting.md) |
| Handover status, scope, and limitations | [docs/customer-handover.md](docs/customer-handover.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

### Contributing and maintaining

| Need | Document |
| --- | --- |
| Contribution workflow | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Guidance for AI/code agents | [AGENTS.md](AGENTS.md) |
| Backend developer reference (project layout, tests) | [MVP_v1/README.md](MVP_v1/README.md) |
| Architecture decision records | [docs/architecture/README.md](docs/architecture/README.md) |

### Course/internal artifacts

The following are course-assignment artifacts (backlog, sprint planning, process, and QA evidence) rather than customer-facing product documentation. They're kept for traceability but aren't required reading to use the product:

[docs/user-stories.md](docs/user-stories.md) · [docs/roadmap.md](docs/roadmap.md) · [docs/development-process.md](docs/development-process.md) · [docs/definition-of-done.md](docs/definition-of-done.md) · [docs/testing.md](docs/testing.md) · [docs/quality-requirements.md](docs/quality-requirements.md) · [docs/quality-requirement-tests.md](docs/quality-requirement-tests.md) · [docs/user-acceptance-tests.md](docs/user-acceptance-tests.md) · [reports/](reports/)

## Repository layout

| Path       | Purpose                                                                                         |
| ---------- | ----------------------------------------------------------------------------------------------- |
| `MVP_v1/`  | Current maintained FastAPI backend, web admin UI, ML service boundary, Docker setup, and tests. |
| `MVP_v0/`  | Historical standalone prototype from the early course stage.                                    |
| `docs/`    | Product documentation (setup, deployment, architecture, configuration, usage) plus process/QA artifacts kept for traceability. |
| `reports/` | Weekly course reports and assignment evidence (historical, not product documentation).          |
| `.github/` | Issue templates, pull request template, and CI workflows.                                       |

## Development and contribution

All non-trivial changes must be made through issue-linked branches and reviewed pull requests. See [CONTRIBUTING.md](CONTRIBUTING.md) for the current workflow, testing commands, review expectations, and documentation update rules.

Before merging a change, make sure the relevant acceptance criteria are verified, CI passes, user-visible changes are reflected in `CHANGELOG.md`, and affected maintained documentation is updated.

## Safety and privacy

Do not commit:

* real credentials or secrets;
* private `.env` files;
* customer-identifying information;
* private recordings or private recording links;
* exact private timecodes;
* production data, real face datasets, or unnecessary personal data.

Use sanitized demo data for public screenshots, reports, releases, and videos.

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE).
