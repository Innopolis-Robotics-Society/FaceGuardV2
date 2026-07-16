# Testing Status

> **For course/internal use.** This is a course QA-evidence artifact, not customer-facing product documentation. For product setup, architecture, and usage, see the documentation index in the root [README.md](../README.md).

## Critical Modules and Coverage

| Critical module | Why critical | Required line coverage | Current line coverage | Evidence |
|---|---|---:|---:|---|
| `app/database.py` | Core user workflow: recognition decisions (US-001, US-011), temporary access lifecycle (US-013), persistence. Defects affect access control decisions. | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| `app/auth.py` | Security: admin registration (US-002), password hashing, session signing. Defects allow unauthorized admin access. | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| `app/recognition.py` | Core user workflow: background poller, ML client interaction, access decision (US-001, US-011). | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| `app/servo.py` | Hardware safety: physical (US-006) and emulated (US-007) door actuation must not hang open. Defects create physical security risk. | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| `app/config.py` | Configuration validation: thresholds (US-008), pins, secrets, servo mode. Affects all runtime behavior. | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| `app/ml_client.py` | ML integration: health probing, frame parsing, embedding extraction. Defects silently drop recognition data. **Added MVP v2.** | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| `app/state.py` | Shared runtime state: verdict fan-out to SSE subscribers, door-open flag, ML health flag. Defects corrupt live UI. **Added MVP v2.** | 30% | TBD | [Coverage report](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |

## Automated Test Status

| Test type | Scope | Command or CI check | Latest result | Evidence |
|---|---|---|---|---|
| Unit tests | Auth, DB, servo, config, recognition, ML client, state — in isolation | `pytest -m "not integration and not qrt"` | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| Integration tests | API routes with TestClient + DB: auth flow, logs API, user/guest CRUD | `pytest -m integration` | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| Automated QRTs | QR-001 … QR-005 | `pytest -m qrt` | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |

## Test File Index

| File | Marks | What it covers |
|---|---|---|
| `test_auth.py` | `qrt`, unit | bcrypt hash/verify — QRT-005 |
| `test_config.py` | unit | Settings validation, env loading |
| `test_database.py` | `qrt`, unit | FaceDatabase CRUD, recognize(), audit log — QRT-001…004, QRT-007 |
| `test_integration.py` | `integration` | healthz, login/logout flow |
| `test_recognition.py` | unit, asyncio | RecognitionLoop tick — granted, denied, idle, error |
| `test_servo.py` | `qrt`, unit | EmulatedServo open/close, make_servo fallback — QRT-006 |
| `test_ml_client.py` | unit, asyncio | MLClient health, get_latest parsing, error handling **[MVP v2]** |
| `test_state.py` | unit, asyncio | SystemState snapshot, update, subscribe, ml_health **[MVP v2]** |
| `test_routes_logs.py` | `integration` | GET /api/logs — auth, schema, limit, filter **[MVP v2]** |
| `test_routes_users.py` | `integration` | delete user/guest, purge expired guests **[MVP v2]** |

## CI and QA Check Status

| Gate or check | Required for Done? | Latest protected-branch status | Evidence |
|---|---|---|---|
| Linting (ruff) | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| Format check (ruff format --check) | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| Type checking (mypy) | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| Build (Docker image) | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| Unit + integration tests | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| Coverage report | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| Automated QRTs | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |
| Additional QA check (dependency vulnerability scan) | Yes | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) |

## Additional QA Check Rationale

| QA objective or risk | Additional QA check | Scope | Latest result | Evidence | Limitations or follow-up |
|---|---|---|---|---|---|
| Dependencies with known vulnerabilities may expose the Raspberry Pi deployment to avoidable risk. | `pip-audit` scans Python dependencies against the PyPI vulnerability database. | `pyproject.toml` / installed packages | Passing | [CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions) | Some vulnerabilities may require manual triage or delayed upstream fixes; no automated fix is applied. |

## Manual Evidence That Does Not Count as QRT

| Evidence | Scope | Result | Follow-up PBI or issue |
|---|---|---|---|
| Customer UAT on Raspberry Pi 4 | End-to-end recognition + servo actuation (US-001, US-006) | Not yet performed | — |

## MVP v2 Test Extension Rationale

Tests were added where the Sprint 3 scope introduced or stabilized new behavior:

| New test file | Trigger |
|---|---|
| `test_ml_client.py` | `MLClient` is the only integration point with the external ML service. Error handling (malformed JSON, network failure, non-200 status) was not previously verified by any automated test. |
| `test_state.py` | `SystemState` drives the live SSE dashboard. The subscriber fan-out, door-open flag, and ML health flag are load-bearing for the UI but had no automated coverage. |
| `test_routes_logs.py` | `/api/logs` was delivered in Sprint 3 (US-010). Auth guard, response schema, and query-parameter validation needed integration-level verification. |
| `test_routes_users.py` | Delete and purge routes were stabilized in Sprint 3. The 404 path and redirect behavior needed explicit integration tests. |
