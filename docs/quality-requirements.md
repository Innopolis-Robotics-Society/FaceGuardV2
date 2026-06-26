# Quality Requirements

FaceGuard quality requirements.

## QR-001: Recognition response time

**ISO/IEC 25010 sub-characteristic:** Time behaviour

**Scenario:** When the backend receives a valid face embedding from the ML service under the standard Docker Compose environment, the system shall produce an access verdict within 1 second for at least 95% of automated test attempts.

**Why this matters:** Access control must respond quickly so a recognized user is not blocked at the door.

**Traceability:** Recognition pipeline, ML service integration, access decision.

**Linked quality requirement tests:** [QRT-001](quality-requirement-tests.md#qrt-001-recognition-response-time)

---

## QR-002: Low-confidence access denial

**ISO/IEC 25010 sub-characteristic:** Integrity

**Scenario:** When the ML service returns no face, an unknown face, or a similarity score below the configured recognition threshold under the backend test environment, the system shall keep the door closed and make zero servo-open calls in 100% of automated test cases. No-face frames shall leave the system in `idle`; unknown or below-threshold faces shall return `denied`.

**Why this matters:** The system must not unlock the door for unknown or low-confidence users.

**Traceability:** No-face handling, threshold comparison, access decision, servo control.

**Linked quality requirement tests:** [QRT-002](quality-requirement-tests.md#qrt-002-low-confidence-access-denial)

---

## QR-003: Safe backend behavior during ML failure

**ISO/IEC 25010 sub-characteristic:** Fault tolerance

**Scenario:** When the ML service is unavailable, unhealthy, or returns no latest frame under the backend integration test environment, the backend shall stay running, return an `error` verdict, keep the door closed, and make zero servo-open calls.

**Why this matters:** If the ML service fails, the system must fail safely instead of crashing or unlocking the door.

**Traceability:** ML health check, ML client latest-frame handling, recognition loop, safe access decision.

**Linked quality requirement tests:** [QRT-003](quality-requirement-tests.md#qrt-003-safe-backend-behavior-during-ml-failure)

---

## Maintenance

These quality requirements are maintained project assets. If product logic, CI, or architecture changes, update this file and `quality-requirement-tests.md`.
