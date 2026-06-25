# User Acceptance Tests

| UAT ID | User Story | Scenario | Steps | Expected Result | Status |
|---|---|---|---|---|---|
| UAT-001 | US-002 | Register a new permanent user | 1. Login as admin. 2. Go to `/register`. 3. Enter name, select Permanent. 4. Click Capture & register. | User appears in `/users` list with averaged embedding. | Not tested |
| UAT-002 | US-006 / US-007 | Servo unlock on recognized face | 1. Register user. 2. Present face to camera. 3. Wait for recognition cycle. | Door opens for `SERVO_OPEN_DURATION_SEC` seconds, then closes automatically (physical servo on Pi, emulated UI on x86). | Not tested |
| UAT-003 | US-008 / US-011 | Threshold tuning and low-confidence lock | 1. Set `THRESHOLD=0.45` in `.env`. 2. Restart. 3. Test registered face (score ≥ 0.45) vs unknown face (score < 0.45). | Registered → granted. Unknown / low confidence → denied, door stays locked. | Not tested |
| UAT-004 | US-010 | Audit log completeness | 1. Perform several access attempts (granted and denied). 2. Open `/logs`. | All attempts listed with timestamp, name, score, access type, result. | Not tested |
| UAT-005 | US-013 | Temporary access expiration | 1. Register a guest with 1-day access. 2. Wait for expiration (or manually set past date). 3. Attempt recognition. | Guest is rejected as Unknown; expired record is purged from active list. | Not tested |
