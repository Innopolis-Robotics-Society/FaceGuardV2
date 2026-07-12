# User Acceptance Tests

## Table of Contents
- [UAT Scenarios](#uat-scenarios)
- [Execution Results — Sprint 2](#execution-results--sprint-2)
- [Execution Results — Sprint 3](#execution-results--sprint-3)
- [Execution Results — Week 6](#execution-results--week-6)

---

## UAT Scenarios

| UAT ID | User Story | Scenario | Steps | Expected Result | Status |
|---|---|---|---|---|---|
| UAT-001 | US-002 | Register a new permanent user | 1. Login as admin. 2. Go to `/register`. 3. Enter name, select Permanent. 4. Click Capture & register. | User appears in `/users` list with averaged embedding. | Active |
| UAT-002 | US-006 / US-007 | Servo unlock on recognized face | 1. Register user. 2. Present face to camera. 3. Wait for recognition cycle. | Door opens for `SERVO_OPEN_DURATION_SEC` seconds, then closes automatically (physical servo on Pi, emulated UI on x86). | Active |
| UAT-003 | US-008 / US-011 | Threshold tuning and low-confidence lock | 1. Set `THRESHOLD=0.45` in `.env`. 2. Restart. 3. Test registered face (score ≥ 0.45) vs unknown face (score &lt; 0.45). | Registered → granted. Unknown / low confidence → denied, door stays locked. | Active |
| UAT-004 | US-010 | Audit log completeness | 1. Perform several access attempts (granted and denied). 2. Open `/logs`. | All attempts listed with timestamp, name, score, access type, result. | Active |
| UAT-005 | US-013 | Temporary access expiration | 1. Register a guest with 1-day access. 2. Wait for expiration (or manually set past date). 3. Attempt recognition. | Guest is rejected as Unknown; expired record is purged from active list. | Active |
| UAT-006 | US-002 / US-013 | Admin deletes a user or guest via web UI | 1. Login as admin. 2. Open `/users` or `/guests` list. 3. Click Delete next to an entry. 4. Confirm deletion. | Entry disappears from the list immediately. Subsequent recognition of that person returns "Unknown". | Active |
| UAT-007 | US-013 | Admin purges all expired guests at once | 1. Register two guests with past expiration dates. 2. Register one guest with a future date. 3. Click "Purge expired" in `/guests`. | Only the two expired guests are removed. Active guest remains. Response confirms count of purged records. | Active |

---

## Execution Results — Sprint 2

**Date:** 2025-06-13
**Participants:** [customer name], [team]
**Recording:** Submitted privately via Moodle

| UAT ID | Scenario | Result | Notes |
|--------|----------|--------|-------|
| UAT-001 | Register a new permanent user | ✅ Pass | — |
| UAT-002 | Servo unlock on recognized face | ✅ Pass | — |
| UAT-004 | Audit log completeness | ✅ Pass | — |
| UAT-005 | Temporary access expiration | ✅ Pass | — |

---

## Execution Results — Sprint 3

**Date:** 2025-07-04
**Participants:** [customer name], [team]
**Recording:** Submitted privately via Moodle

| UAT ID | Scenario | Result | Notes |
|--------|----------|--------|-------|
| UAT-001 | Register a new permanent user | ✅ Pass | Re-verified after data layer refactor |
| UAT-002 | Servo unlock on recognized face | ✅ Pass | — |
| UAT-003 | Threshold tuning and low-confidence lock | ✅ Pass | Tested with threshold=0.45 |
| UAT-004 | Audit log completeness | ✅ Pass | — |
| UAT-005 | Temporary access expiration | ✅ Pass | — |
| UAT-006 | Admin deletes user/guest via web UI | ✅ Pass | — |
| UAT-007 | Admin purges expired guests | ✅ Pass | — |

### Key Feedback
- Admin found the delete confirmation flow intuitive and fast.
- Customer confirmed audit log filtering by name and date works as expected.

### Resulting PBIs
- No critical defects found. Minor UX suggestions deferred to backlog.

---

## Execution Results — Week 6

**Date:** 2026-07-12
**Participants:** [customer name], Egor Shkil, Mikhail Brovkin
**Recording:** Submitted privately via Moodle

| UAT ID | Scenario | Result | Notes |
|--------|----------|--------|-------|
| UAT-001 | Register a new permanent user | ✅ Pass | Re-verified after backend optimization |
| UAT-002 | Servo unlock on recognized face | ✅ Pass | Re-verified; liveness detection fix confirmed (anti-spoofing active) |
| UAT-003 | Threshold tuning and low-confidence lock | ✅ Pass | Re-verified after backend optimization; threshold stability confirmed under load |
| UAT-004 | Audit log completeness | ✅ Pass | Re-verified after backend optimization |
| UAT-005 | Temporary access expiration | ✅ Pass | Re-verified after backend optimization |
| UAT-006 | Admin deletes user/guest via web UI | ✅ Pass | Re-verified after backend optimization |
| UAT-007 | Admin purges expired guests | ✅ Pass | Re-verified after backend optimization |

### Public UAT Result Summary — Week 6

**Scenarios Passed:**  
All 7 active UAT scenarios (UAT-001 through UAT-007) passed successfully.

**Scenarios Failed / Need Changes:**  
None.

**Key Feedback Points:**
- Backend performance optimizations confirmed — recognition cycle latency reduced, UI responsiveness improved.
- Liveness detection fix verified — the system correctly rejects static photos and masks, granting access only to live faces.
- Admin flows (user deletion, guest purge) remain intuitive and fast.

**Resulting PBIs / Issues:**
- No critical defects or product gaps identified.
- Minor UX suggestions remain deferred in the product backlog.
