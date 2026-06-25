# Quality Requirements

| ID | Requirement | Priority | Source |
|---|---|---|---|
| QR-001 | The system shall match registered users with cosine similarity ≥ THRESHOLD and reject unknown or low-confidence persons (score < THRESHOLD). | Must have | US-001, US-011 |
| QR-002 | The system shall not grant access to users whose temporary access has expired; expired profiles must be excluded from recognition and purged. | Must have | US-013 |
| QR-003 | Admin passwords shall be stored as salted bcrypt hashes; plaintext shall never be persisted. | Must have | Security |
| QR-004 | The servo shall automatically close the door within SERVO_OPEN_DURATION_SEC + 1 s to prevent an indefinite open state. | Must have | US-006, US-007 |
| QR-005 | Every access attempt (granted or denied) shall be written to the audit log with timestamp, name, score, access type, and result. | Must have | US-010 |
