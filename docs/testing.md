# Testing Status

## Critical Modules and Coverage

| Critical module | Why critical | Required line coverage | Current line coverage | Evidence |
|---|---|---:|---:|---|
| `app/database.py` | Core user workflow: recognition decisions (US-001, US-011), temporary access lifecycle (US-013), persistence. Defects affect access control decisions. | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| `app/auth.py` | Security: admin registration (US-002), password hashing, session signing. Defects allow unauthorized admin access. | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| `app/recognition.py` | Core user workflow: background poller, ML client interaction, access decision (US-001, US-011). | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| `app/servo.py` | Hardware safety: physical (US-006) and emulated (US-007) door actuation must not hang open. Defects create physical security risk. | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| `app/config.py` | Configuration validation: thresholds (US-008), pins, secrets, servo mode. Affects all runtime behavior. | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |

## Automated Test Status

| Test type | Scope | Command or CI check | Latest result | Evidence |
|---|---|---|---|---|
| Unit tests | Auth, DB, servo, config, recognition in isolation | `pytest -m "not integration and not qrt"` | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| Integration tests | API routes with TestClient + DB | `pytest -m integration` | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| Automated QRTs | QR-001 … QR-005 | `pytest -m qrt` | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |

## CI and QA Check Status

| Gate or check | Required for Done? | Latest protected-branch status | Evidence |
|---|---|---|---|
| Linting (ruff) | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| Format check (ruff format --check) | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| Type checking (mypy) | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| Build (Docker image) | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| Unit + integration tests | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| Coverage report | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| Automated QRTs | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |
| Additional QA check (dependency vulnerability scan) | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) |

## Additional QA Check Rationale

| QA objective or risk | Additional QA check | Scope | Latest result | Evidence | Limitations or follow-up |
|---|---|---|---|---|---|
| Dependencies with known vulnerabilities may expose the Raspberry Pi deployment to avoidable risk. | `pip-audit` scans Python dependencies against the PyPI vulnerability database. | `pyproject.toml` / installed packages | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/RUN_ID) | Some vulnerabilities may require manual triage or delayed upstream fixes; no automated fix is applied. |

## Manual Evidence That Does Not Count as QRT

| Evidence | Scope | Result | Follow-up PBI or issue |
|---|---|---|---|
| Customer UAT on Raspberry Pi 4 | End-to-end recognition + servo actuation (US-001, US-006) | Not yet performed | — |

| Dependencies with known vulnerabilities may expose the Raspberry Pi deployment to avoidable risk. | `pip-audit` scans Python dependencies against the PyPI vulnerability database. | `pyproject.toml` / installed packages | **21 vulnerabilities found** (jinja2, pillow, python-multipart, starlette) — see CI log for details | CI run | Fix versions identified; upgrade tracked in follow-up issue. |
