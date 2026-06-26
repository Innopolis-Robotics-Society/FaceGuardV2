# Quality Requirement Tests

Automated quality requirement tests for FaceGuardV2 Assignment 4.

## QRT index

| QRT ID | Linked QR | Test type | Test location | CI command |
|---|---|---|---|---|
| QRT-001 | QR-001 | Automated performance test | `tests/quality/test_recognition_response_time.py` | `python -m pytest tests/quality/test_recognition_response_time.py` |
| QRT-002 | QR-002 | Automated unit test | `tests/quality/test_low_confidence_denial.py` | `python -m pytest tests/quality/test_low_confidence_denial.py` |
| QRT-003 | QR-003 | Automated integration test | `tests/quality/test_ml_failure_safety.py` | `python -m pytest tests/quality/test_ml_failure_safety.py` |

---

## QRT-001: Recognition response time

**Linked quality requirement:** QR-001

**Verification method:** Automated pytest performance test.

**Test data, setup, or environment:** Standard CI environment with mocked ML response containing one valid face embedding and one registered user in the test database.

**Automated command or CI check:**

```bash
python -m pytest tests/quality/test_recognition_response_time.py
```

**Expected measurable result:** At least 95% of recognition attempts produce an access verdict in 1 second or less.

**Evidence location:** Latest protected default-branch CI run, pytest job logs, and Week 4 testing screenshots in `reports/week4/images/`.

---

## QRT-002: Low-confidence access denial

**Linked quality requirement:** QR-002

**Verification method:** Automated pytest unit test.

**Test data, setup, or environment:** Backend test environment with mocked ML responses for no face, unknown face, and embedding score below the configured recognition threshold.

**Automated command or CI check:**

```bash
python -m pytest tests/quality/test_low_confidence_denial.py
```

**Expected measurable result:** 100% of no-face, low-confidence, and unknown-face cases keep the door closed and make zero servo-open calls. The no-face case returns `idle`; low-confidence and unknown-face cases return `denied`.

**Evidence location:** Latest protected default-branch CI run, pytest job logs, and Week 4 testing screenshots in `reports/week4/images/`.

---

## QRT-003: Safe backend behavior during ML failure

**Linked quality requirement:** QR-003

**Verification method:** Automated pytest integration test.

**Test data, setup, or environment:** Backend test environment with mocked unhealthy ML service, missing latest frame, and failed ML health result.

**Automated command or CI check:**

```bash
python -m pytest tests/quality/test_ml_failure_safety.py
```

**Expected measurable result:** Backend returns an `error` verdict for each ML failure case, keeps the door closed, and makes zero servo-open calls.

**Evidence location:** Latest protected default-branch CI run, pytest job logs, and Week 4 testing screenshots in `reports/week4/images/`.

---

## CI requirement

All QRTs must run in the main CI pipeline before merge:

```bash
python -m pytest tests/quality/
```

A PBI that changes recognition, threshold logic, ML integration, or servo behavior cannot be marked Done if any linked QRT fails.

## Maintenance

These QRTs are maintained project assets. If a quality requirement changes, update the linked QRT and CI command.
