# Quality Requirement Tests

## Table of Contents

1. [QRT-001: Registered user recognition](#qrt-001-registered-user-recognition)
2. [QRT-002: Unknown user below threshold](#qrt-002-unknown-user-below-threshold)
3. [QRT-003: Best-match selection](#qrt-003-best-match-selection)
4. [QRT-004: Expired guest denial](#qrt-004-expired-guest-denial)
5. [QRT-005: Password hash verification](#qrt-005-password-hash-verification)
6. [QRT-006: Emulated servo open/close](#qrt-006-emulated-servo-openclose)
7. [QRT-007: Recognition audit log](#qrt-007-recognition-audit-log)
8. [QRT-008: ML client fault tolerance](#qrt-008-ml-client-fault-tolerance)
9. [QRT-009: Logs API correctness](#qrt-009-logs-api-correctness)

---

## Summary table

| QRT ID | Target QR | Test file | Test function | How to run |
|---|---|---|---|---|
| QRT-001 | QR-001 | `tests/test_database.py` | `test_recognize_matches_registered_user_above_threshold` | `pytest -m qrt` |
| QRT-002 | QR-001 | `tests/test_database.py` | `test_recognize_returns_unknown_below_threshold` | `pytest -m qrt` |
| QRT-003 | QR-001 | `tests/test_database.py` | `test_recognize_picks_best_match_when_multiple_users` | `pytest -m qrt` |
| QRT-004 | QR-002 | `tests/test_database.py` | `test_recognize_ignores_expired_guests` | `pytest -m qrt` |
| QRT-005 | QR-003 | `tests/test_auth.py` | `test_hash_and_verify_roundtrip` | `pytest -m qrt` |
| QRT-006 | QR-004 | `tests/test_servo.py` | `test_emulated_servo_opens_then_closes` | `pytest -m qrt` |
| QRT-007 | QR-005 | `tests/test_database.py` | `test_recognize_writes_audit_log` | `pytest -m qrt` |
| QRT-008 | QR-006 | `tests/test_ml_client.py` | see detail below | `pytest tests/test_ml_client.py -v` |
| QRT-009 | QR-007 | `tests/test_routes_logs.py` | see detail below | `pytest -m integration tests/test_routes_logs.py -v` |

---

## QRT-001: Registered user recognition

**Linked quality requirement:** [QR-001](quality-requirements.md#qr-001-correct-face-recognition-decision)

**What is verified:** When a probe embedding identical to a registered user's embedding is passed to `recognize()`, the function returns that user's name, `access_type = "user"`, and a score >= 0.99.

**Test file:** `tests/test_database.py`

**Test function:** `test_recognize_matches_registered_user_above_threshold`

**How to run:**

```
cd MVP_v1
pytest -m qrt -v
```

---

## QRT-002: Unknown user below threshold

**Linked quality requirement:** [QR-001](quality-requirements.md#qr-001-correct-face-recognition-decision)

**What is verified:** When a probe embedding that is very different from all registered embeddings is passed to `recognize()` with a high threshold, the function returns `name = "Unknown"`, `access_type = "unknown"`, and `matched_user_id = None`.

**Test file:** `tests/test_database.py`

**Test function:** `test_recognize_returns_unknown_below_threshold`

**How to run:**

```
cd MVP_v1
pytest -m qrt -v
```

---

## QRT-003: Best-match selection

**Linked quality requirement:** [QR-001](quality-requirements.md#qr-001-correct-face-recognition-decision)

**What is verified:** When multiple users are registered and the probe matches one of them exactly, `recognize()` returns that specific user and not any other.

**Test file:** `tests/test_database.py`

**Test function:** `test_recognize_picks_best_match_when_multiple_users`

**How to run:**

```
cd MVP_v1
pytest -m qrt -v
```

---

## QRT-004: Expired guest denial

**Linked quality requirement:** [QR-002](quality-requirements.md#qr-002-expired-guest-access-denial)

**What is verified:** When a guest's access period has expired, `recognize()` does not match that guest even if the probe embedding is identical, and returns `access_type = "unknown"`.

**Test file:** `tests/test_database.py`

**Test function:** `test_recognize_ignores_expired_guests`

**How to run:**

```
cd MVP_v1
pytest -m qrt -v
```

---

## QRT-005: Password hash verification

**Linked quality requirement:** [QR-003](quality-requirements.md#qr-003-secure-password-verification)

**What is verified:** `hash_password()` produces a hash that `verify_password()` accepts for the correct password and rejects for any other password. Plain text is never stored or compared.

**Test file:** `tests/test_auth.py`

**Test function:** `test_hash_and_verify_roundtrip`

**How to run:**

```
cd MVP_v1
pytest -m qrt -v
```

---

## QRT-006: Emulated servo open/close

**Linked quality requirement:** [QR-004](quality-requirements.md#qr-004-servo-emulator-operability)

**What is verified:** `EmulatedServo.open()` sets `is_open = True`; after the configured duration elapses the servo automatically closes and `last_event["action"] == "closed"`.

**Test file:** `tests/test_servo.py`

**Test function:** `test_emulated_servo_opens_then_closes`

**How to run:**

```
cd MVP_v1
pytest -m qrt -v
```

---

## QRT-007: Recognition audit log

**Linked quality requirement:** [QR-005](quality-requirements.md#qr-005-recognition-audit-logging)

**What is verified:** After two `recognize()` calls (one granted, one denied), `list_logs()` returns exactly two entries with correct `success`, `access_type`, and `name` values, ordered most-recent-first.

**Test file:** `tests/test_database.py`

**Test function:** `test_recognize_writes_audit_log`

**How to run:**

```
cd MVP_v1
pytest -m qrt -v
```

---

## QRT-008: ML client fault tolerance

**Linked quality requirement:** [QR-006](quality-requirements.md#qr-006-ml-client-fault-tolerance)

**What is verified:** `MLClient` returns safe fallback values (`False` or `None`) on network errors, non-200 HTTP responses, and malformed JSON without raising exceptions. Individual malformed face entries are skipped without dropping the entire frame.

**Test file:** `tests/test_ml_client.py`

**Automated checks:**

| Test function | Scenario | Expected result |
|---|---|---|
| `test_health_returns_true_on_200` | ML service responds 200 | `health()` returns `True` |
| `test_health_returns_false_on_503` | ML service responds 503 | `health()` returns `False` |
| `test_health_returns_false_on_connection_error` | Network refused | `health()` returns `False`, no exception raised |
| `test_get_latest_returns_none_on_404` | ML service responds 404 | `get_latest()` returns `None` |
| `test_get_latest_returns_none_on_non_json` | Body is not valid JSON | `get_latest()` returns `None` |
| `test_get_latest_skips_malformed_face_entry` | One face entry has bad structure | Valid faces parsed; bad entry skipped silently |
| `test_get_latest_returns_none_on_network_error` | Network refused | `get_latest()` returns `None`, no exception raised |

**How to run:**

```
cd MVP_v1
pytest tests/test_ml_client.py -v
```

**CI job:** `test-and-coverage`

---

## QRT-009: Logs API correctness

**Linked quality requirement:** [QR-007](quality-requirements.md#qr-007-logs-api-correctness)

**What is verified:** `GET /api/logs` requires authentication, returns the correct JSON schema, and enforces `limit` and `q` query parameters including HTTP 422 for out-of-range `limit` values.

**Test file:** `tests/test_routes_logs.py`

**Automated checks:**

| Test function | Scenario | Expected result |
|---|---|---|
| `test_logs_requires_auth` | No session cookie | 302/401/403 — access denied |
| `test_logs_returns_entries_list_when_empty` | Authenticated, empty DB | `{"entries": []}` with status 200 |
| `test_log_entry_schema` | One log entry in DB | Entry contains id, name, score, access_type, success, timestamp |
| `test_logs_limit_parameter_respected` | 10 entries, limit=3 | 3 or fewer entries returned |
| `test_logs_filter_by_name` | Alice and Bob entries, q=Alice | Only Alice entries returned |
| `test_logs_invalid_limit_rejected` | limit=0 (below minimum ge=1) | HTTP 422 Unprocessable Entity |
| `test_logs_limit_too_large_rejected` | limit=9999 (above maximum le=1000) | HTTP 422 Unprocessable Entity |

**How to run:**

```
cd MVP_v1
pytest tests/test_routes_logs.py -v -m integration
```

**CI job:** `test-and-coverage`
