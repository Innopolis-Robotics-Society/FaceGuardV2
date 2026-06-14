# Customer Meeting Summary

**Date:** June 2026  
**Participants:** Dmitry, Egor, Nadezhda, Customer

## Purpose

The purpose of the meeting was to clarify system requirements, define the MVP scope, review implementation ideas, and validate user stories for the Face Recognition Access Control System.

---

## Requirements Clarification

### Temporary Access Control

The customer confirmed that the system must support configurable access duration during user registration:

- Permanent access
- Access valid until a specific date
- Access valid for a predefined time period

The administrator should be able to configure these settings when creating a user account.

### Liveness Detection

The minimum requirement is protection against photo spoofing attacks.

The team should also test whether the system can be bypassed using video playback. If vulnerabilities are found, additional liveness detection mechanisms may be considered in future versions.

### User Feedback

The customer suggested adding LED indicators to provide visual feedback:

| Indicator | Meaning |
|------------|------------|
| Green | Access granted |
| Red | Access denied |
| Yellow | System calibration or processing |

The customer can provide the necessary LEDs.

### Lighting Conditions

The system will be installed in a basement environment with artificial lighting.

Additional lighting may be added if testing shows that image quality is insufficient for reliable recognition.

### Failed Access Attempts

Instead of maintaining a blacklist, the customer requested logging repeated unsuccessful recognition attempts.

The system should highlight situations where the same unknown person repeatedly attempts to gain access.

### Multiple-Person Scenario

Handling multiple people simultaneously is outside the scope of the MVP.

Users should approach the camera individually and complete verification one at a time.

### Camera Placement

Recommended installation height:

- 1.60–1.70 meters above the floor.

---

## MVP Scope

The team proposed the following MVP functionality:

- User database containing:
  - ID
  - Name
  - Face embedding
- Backend CRUD operations
- User registration using five captured images
- Generation of an averaged normalized embedding
- Face recognition through embedding comparison
- Similarity score calculation
- Access grant/deny decision
- Initial deployment in an emulator environment

The customer approved the proposed MVP scope.

---

## MVP v0 Clarification

The customer clarified that MVP v0 should represent a prototype demonstrating the core concept and user interaction flow.

The current implementation approach was approved:

1. Detect a face using OpenCV.
2. Extract a face embedding using InsightFace.
3. Compare the embedding with stored vectors.
4. Output an access decision.

This implementation is considered an acceptable MVP v0 deliverable.

---

## User Stories Review

The team reviewed all proposed user stories with the customer.

**Decision:** All user stories were approved without modifications.

---

## Action Items

- Implement configurable access duration settings.
- Develop photo spoof detection.
- Test system resistance to video spoofing attacks.
- Add logging for repeated failed access attempts.
- Integrate LED status indicators.
- Test the system under real lighting conditions.
- Continue development of the approved MVP prototype.

---

## Conclusion

The customer approved:

- Functional requirements;
- MVP scope;
- Prototype implementation approach;
- All proposed user stories.

The team can proceed with development according to the agreed requirements.
