# MVPv0 Report

## Purpose and description of the MVP v0 foundation
Show the minimum version of the product (the technical part of the work scheme, approximately what it will look like) to the customer

## Deployment URL or runnable-artifact link
[MVPv0 builded release](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/download/v0.0.0/FaceVerification.zip)
[Source code](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/pull/5)

## Public video demonstration link
https://drive.google.com/file/d/1ttbY5ay20juh_uStaIQ6FwdaV638wXiO/view?usp=sharing

## Relationship to the prototype and proposed MVP v1 stories

### Prototype
MVP v0 is the prototype for the graphical interface: the same OpenCV window streams the webcam, detects a face via InsightFace, compares it against hard-coded embeddings, and shows verdict.  
The CLI (`register`, `remove`, `logs`, etc.) is documented in `docs/interface.md` but not implemented in MVP v0.

### MVP v1 stories

| Story | What MVP v0 provides | What is missing |
|-------|----------------------|-----------------|
| **US-01** Automatic unlock | Real-time face recognition | Hardware signal to servo/LED (Raspberry Pi GPIO not yet integrated) |
| **US-02** User registration | Working embedding extraction from live camera | Database, multi-angle capture UI, admin flow |
| **US-03** Temporary visitor access | - | Entire visitor logic, time-limited access, DB schema |
| **US-04** Docker packaging | None | Dockerfile, multi-arch build (ARM, x86) |
| **US-05** GUI feedback | Basic OpenCV text overlay | Polished UI with confidence metrics and name display |
| **US-06** Physical servo | None | GPIO servo control on Raspberry Pi 5 |
| **US-07** Cross-platform servo emulation | x86 build runs and renders visual feedback | Abstracted actuator wrapper that swaps GUI servo for GPIO on ARM |
| **US-08** Threshold tuning | Hard-coded threshold | Labelled dataset evaluation, precision/recall curves |
| **US-09** Liveness detection | None | Anti-spoofing module |
| **US-10** Audit logging | None | Structured logging of attempts, failure categories, confidence scores |


## Current limitations, placeholders, and mocks

- **Hard-coded embeddings** - no database or runtime registration.
- **No hardware actuation** - servo/LED absent; only onscreen text changes. No GPIO
- **x86-only** - Windows only; Raspberry Pi and Linux untested.
- **No persistence** - no users DB, no logs, no audit trail.
- **No liveness detection** - photos/screens can spoof the system.
- **No admin CLI** - not implemented.
- **No Docker** - no containerization, no multi-arch build.

**Mocks:**
- Guests: treated as permanent users; no expiry logic.
- Logs: ---


## Link to local setup instructions
See [local setup instructions](../../README.md).

## Repeatable smoke-check scenario

**Artifact:** Pre-built Windows executable FaceVerification.exe
**Location:** GitHub Releases -> [FaceGuard MVP v0](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/tag/v0.0.0)

**Steps:**
1. **Download** *FaceVerification.exe* from the release page.
2. **Run** - double-click the file
4. **Observe the OpenCV window:**
Shown in the video demonstration. When the user is known a frame around the user's face is green, otherwise it is red. Therefore, we can health check
5. **Exit**
