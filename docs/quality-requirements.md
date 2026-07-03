# Quality Requirements

FaceGuardV2 quality requirements for Assignment 4.

## QR index

| QR ID | Title | ISO/IEC 25010 sub-characteristic | Linked QRT | Related ADRs |
|---|---|---|---|---|
| QR-001 | Correct face recognition decision | Functional correctness | [QRT-001](quality-requirement-tests.md#qrt-001-registered-user-recognition), [QRT-002](quality-requirement-tests.md#qrt-002-unknown-user-below-threshold), [QRT-003](quality-requirement-tests.md#qrt-003-best-match-selection) | [ADR-001](architecture/adr/ADR-001-separate-backend-and-ml-service.md) |
| QR-002 | Expired guest access denial | Integrity | [QRT-004](quality-requirement-tests.md#qrt-004-expired-guest-denial) | [ADR-002](architecture/adr/ADR-002-use-sqlite-through-face-database.md) |
| QR-003 | Secure password verification | Confidentiality | [QRT-005](quality-requirement-tests.md#qrt-005-password-hash-verification) | [ADR-003](architecture/adr/ADR-003-session-auth-and-password-hashing.md) |
| QR-004 | Servo emulator operability | Operability | [QRT-006](quality-requirement-tests.md#qrt-006-emulated-servo-open-close) | [ADR-004](architecture/adr/ADR-004-servo-abstraction-with-emulated-mode.md) |
| QR-005 | Recognition audit logging | Accountability | [QRT-007](quality-requirement-tests.md#qrt-007-recognition-audit-log) | [ADR-002](architecture/adr/ADR-002-use-sqlite-through-face-database.md) |

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

## Maintenance

These quality requirements are maintained project assets. If tests, access logic, authentication, or servo behavior change, update this file and `docs/quality-requirement-tests.md`.
