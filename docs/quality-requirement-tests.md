# Quality Requirement Tests

| QRT ID | Target QR | Test file | Test function | How to run |
|---|---|---|---|---|
| QRT-001 | QR-001 | `tests/test_database.py` | `test_recognize_matches_registered_user_above_threshold` | `pytest -m qrt` |
| QRT-002 | QR-001 | `tests/test_database.py` | `test_recognize_returns_unknown_below_threshold` | `pytest -m qrt` |
| QRT-003 | QR-001 | `tests/test_database.py` | `test_recognize_picks_best_match_when_multiple_users` | `pytest -m qrt` |
| QRT-004 | QR-002 | `tests/test_database.py` | `test_recognize_ignores_expired_guests` | `pytest -m qrt` |
| QRT-005 | QR-003 | `tests/test_auth.py` | `test_hash_and_verify_roundtrip` | `pytest -m qrt` |
| QRT-006 | QR-004 | `tests/test_servo.py` | `test_emulated_servo_opens_then_closes` | `pytest -m qrt` |
| QRT-007 | QR-005 | `tests/test_database.py` | `test_recognize_writes_audit_log` | `pytest -m qrt` |
