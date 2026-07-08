# FaceGuardV2

FaceGuardV2 is a face-recognition access-control system for a laboratory door. It runs as a FastAPI web admin application with a separate ML service for camera-based face detection and embedding extraction, SQLite persistence, audit logging, and servo-door control on Raspberry Pi or emulated hardware.

## Current product access

* **Current product release:** [Latest GitHub Release](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/latest)
* **Product access / run instructions:** [MVP_v1/README.md](MVP_v1/README.md)
* **Current maintained documentation:** [docs/](docs/)
* **Current handover guidance:** [docs/customer-handover.md](docs/customer-handover.md)

> For private deployment credentials, customer-specific access details, or instructor-only evidence, use the private Moodle submission channel. Do not commit private credentials or customer-identifying information to this repository.

## Product status

The current course version is focused on a customer-usable access-control prototype:

* admin login and protected web interface;
* live camera stream through the backend;
* user and temporary guest registration;
* face-recognition decision flow using stored embeddings;
* access audit logging;
* user and guest management;
* servo actuation in GPIO mode on Raspberry Pi or emulated mode for local development;
* Docker Compose based local and Raspberry Pi deployment.

Historical prototype code is kept in `MVP_v0/`. The maintained backend and web admin product lives in `MVP_v1/`.

## Quick start

For the full setup and deployment guide, use [MVP_v1/README.md](MVP_v1/README.md).

Local development with Docker Compose:

```bash
cd MVP_v1
cp .env.example .env
# edit SECRET_KEY, ADMIN_PASSWORD, and other environment values
docker compose up --build
```

Then open:

```text
http://localhost:8000/login
```

For Raspberry Pi deployment, configure `.env` for GPIO mode, connect the servo to the documented BCM pin, and run the Docker Compose stack as described in [MVP_v1/README.md](MVP_v1/README.md).

## Main documentation

| Need                                                           | Document                                                               |
| -------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Customer handover state, access, transition scope, limitations | [docs/customer-handover.md](docs/customer-handover.md)                 |
| Setup, run, API, configuration, user flows                     | [MVP_v1/README.md](MVP_v1/README.md)                                   |
| Architecture and ADRs                                          | [docs/architecture/README.md](docs/architecture/README.md)             |
| User stories and product scope traceability                    | [docs/user-stories.md](docs/user-stories.md)                           |
| Roadmap and course outcome                                     | [docs/roadmap.md](docs/roadmap.md)                                     |
| Definition of Done                                             | [docs/definition-of-done.md](docs/definition-of-done.md)               |
| Testing status and CI evidence                                 | [docs/testing.md](docs/testing.md)                                     |
| Quality requirements                                           | [docs/quality-requirements.md](docs/quality-requirements.md)           |
| Quality requirement tests                                      | [docs/quality-requirement-tests.md](docs/quality-requirement-tests.md) |
| User acceptance tests                                          | [docs/user-acceptance-tests.md](docs/user-acceptance-tests.md)         |
| Contribution workflow                                          | [CONTRIBUTING.md](CONTRIBUTING.md)                                     |
| Guidance for AI/code agents                                    | [AGENTS.md](AGENTS.md)                                                 |
| Changelog                                                      | [CHANGELOG.md](CHANGELOG.md)                                           |

## Repository layout

| Path       | Purpose                                                                                         |
| ---------- | ----------------------------------------------------------------------------------------------- |
| `MVP_v1/`  | Current maintained FastAPI backend, web admin UI, ML service boundary, Docker setup, and tests. |
| `MVP_v0/`  | Historical standalone prototype from the early course stage.                                    |
| `docs/`    | Maintained product, process, architecture, testing, quality, UAT, and handover documentation.   |
| `reports/` | Weekly public reports and assignment evidence indexes.                                          |
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
