# Quality Requirements

> **For course/internal use.** This is a course quality-engineering artifact, not customer-facing product documentation. For product setup, architecture, and usage, see the documentation index in the root [README.md](../README.md).

FaceGuardV2 quality requirements.

## Table of Contents

1. [QR index](#qr-index)
2. [QR-001: Correct face recognition decision](#qr-001-correct-face-recognition-decision)
3. [QR-002: Expired guest access denial](#qr-002-expired-guest-access-denial)
4. [QR-003: Secure password verification](#qr-003-secure-password-verification)
5. [QR-004: Servo emulator operability](#qr-004-servo-emulator-operability)
6. [QR-005: Recognition audit logging](#qr-005-recognition-audit-logging)
7. [QR-006: ML client fault tolerance](#qr-006-ml-client-fault-tolerance)
8. [QR-007: Logs API correctness](#qr-007-logs-api-correctness)
9. [Maintenance](#maintenance)

## QR index

| QR ID | Title | ISO/IEC 25010 sub-characteristic | Linked QRT | Related ADRs |
|---|---|---|---|---|
| QR-001 | Correct face recognition decision | Functional correctness | [QRT-001](quality-requirement-tests.md#qrt-001-registered-user-recognition), [QRT-002](quality-requirement-tests.md#qrt-002-unknown-user-below-threshold), [QRT-003](quality-requirement-tests.md#qrt-003-best-match-selection) | [ADR-001](architecture/adr/ADR-001-separate-backend-and-ml-service.md) |
| QR-002 | Expired guest access denial | Integrity | [QRT-004](quality-requirement-tests.md#qrt-004-expired-guest-denial) | [ADR-002](architecture/adr/ADR-002-use-sqlite-through-face-database.md) |
| QR-003 | Secure password verification | Confidentiality | [QRT-005](quality-requirement-tests.md#qrt-005-password-hash-verification) | [ADR-003](architecture/adr/ADR-003-session-auth-and-password-hashing.md) |
| QR-004 | Servo emulator operability | Operability | [QRT-006](quality-requirement-tests.md#qrt-006-emulated-servo-open-close) | [ADR-004](architecture/adr/ADR-004-servo-abstraction-with-emulated-mode.md) |
| QR-005 | Recognition audit logging | Accountability | [QRT-007](quality-requirement-tests.md#qrt-007-recognition-audit-log) | [ADR-002](architecture/adr/ADR-002-use-sqlite-through-face-database.md) |
| QR-006 | ML client fault tolerance | Fault tolerance | [QRT-008](quality-requirement-tests.md#qrt-008-ml-client-fault-tolerance) | [ADR-001](architecture/adr/ADR-001-separate-backend-and-ml-service.md) |
| QR-007 | Logs API correctness | Functional correctness | [QRT-009](quality-requirement-tests.md#qrt-009-logs-api-correctness) | [ADR-002](architecture/adr/ADR-002-use-sqlite-through-face-database.md) |

---

## QR-001: Correct face recognition decision

**ISO/IEC 25010 sub-characteristic:** Functional correctness

**Scenario:** When the database recognition function receives a face embedding under the automated test environment, it shall return the registered user above threshold, return unknown below threshold, and select the best match when several users exist.

**Why this matters:** FaceGuardV2 must make correct access decisions based on face embeddings.

**Linked quality requirement tests:** [QRT-001](quality-requirement-tests.md#qrt-001-registered-user-recognition), [QRT-002](quality-requirement-tests.md#qrt-002-unknown-user-below-threshold), [QRT-003](quality-requirement-tests.md#qrt-003-best-match-selection)

**Related ADRs:** [ADR-001 Separate backend and ML service](architecture/adr/ADR-001-separate-backend-and-ml-service.md)

---

## QR-002: Expired guest access denial

**ISO/IEC 25010 sub-characteristic:** Integrity

**Scenario:** When recognition finds a guest whose access period has expired under the automated test environment, the system shall not grant access to that guest.

**Why this matters:** Expired guest permissions must not allow unauthorized access.

**Linked quality requirement tests:** [QRT-004](quality-requirement-tests.md#qrt-004-expired-guest-denial)

**Related ADRs:** [ADR-002 Use SQLite through FaceDatabase DAL](architecture/adr/ADR-002-use-sqlite-through-face-database.md)

---

## QR-003: Secure password verification

**ISO/IEC 25010 sub-characteristic:** Confidentiality

**Scenario:** When a password is hashed under the automated test environment, the system shall verify the correct password and reject an incorrect password without storing or comparing plain text passwords.

**Why this matters:** Admin authentication must protect credentials.

**Linked quality requirement tests:** [QRT-005](quality-requirement-tests.md#qrt-005-password-hash-verification)

**Related ADRs:** [ADR-003 Use session authentication and password hashing](architecture/adr/ADR-003-session-auth-and-password-hashing.md)

---

## QR-004: Servo emulator operability

**ISO/IEC 25010 sub-characteristic:** Operability

**Scenario:** When the emulated servo is opened and then closed under the automated test environment, it shall correctly switch between open and closed states.

**Why this matters:** The team and customer must be able to test access-control behavior without physical hardware.

**Linked quality requirement tests:** [QRT-006](quality-requirement-tests.md#qrt-006-emulated-servo-open-close)

**Related ADRs:** [ADR-004 Use servo abstraction with emulated mode](architecture/adr/ADR-004-servo-abstraction-with-emulated-mode.md)

---

## QR-005: Recognition audit logging

**ISO/IEC 25010 sub-characteristic:** Accountability

**Scenario:** When recognition is executed under the automated test environment, the system shall write an audit log entry for the access attempt.

**Why this matters:** Access attempts must be traceable for review and security analysis.

**Linked quality requirement tests:** [QRT-007](quality-requirement-tests.md#qrt-007-recognition-audit-log)

**Related ADRs:** [ADR-002 Use SQLite through FaceDatabase DAL](architecture/adr/ADR-002-use-sqlite-through-face-database.md)

---

## QR-006: ML client fault tolerance

**ISO/IEC 25010 sub-characteristic:** Fault tolerance

**Scenario:** When the ML service is unreachable, returns a non-200 status, or returns a malformed JSON body, `MLClient.health()` and `MLClient.get_latest()` shall return `False` or `None` respectively without raising an exception, and the recognition loop shall set the system state to `error` without crashing.

**Why this matters:** The ML service runs as a separate process and may be temporarily unavailable (camera warm-up, Raspberry Pi reboot). The backend must degrade gracefully rather than crash or hang.

**Linked quality requirement tests:** [QRT-008](quality-requirement-tests.md#qrt-008-ml-client-fault-tolerance)

**Related ADRs:** [ADR-001 Separate backend and ML service](architecture/adr/ADR-001-separate-backend-and-ml-service.md)

---

## QR-007: Logs API correctness

**ISO/IEC 25010 sub-characteristic:** Functional correctness

**Scenario:** When an authenticated admin queries `GET /api/logs`, the endpoint shall return a JSON object with an `entries` array where each entry contains `id`, `name`, `score`, `access_type`, `success`, and `timestamp`. The `limit` and `q` query parameters shall be enforced: `limit` outside `[1, 1000]` shall return HTTP 422; `q` shall filter results to the named user only.

**Why this matters:** The logs view is the primary audit interface for the admin. Incorrect filtering or a broken response schema would make the audit trail unusable.

**Linked quality requirement tests:** [QRT-009](quality-requirement-tests.md#qrt-009-logs-api-correctness)

**Related ADRs:** [ADR-002 Use SQLite through FaceDatabase DAL](architecture/adr/ADR-002-use-sqlite-through-face-database.md)

---

## Maintenance

These quality requirements are maintained project assets. If tests, access logic, authentication, ML client behavior, or servo behavior change, update this file and `docs/quality-requirement-tests.md`.
