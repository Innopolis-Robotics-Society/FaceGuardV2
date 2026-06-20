# Product Roadmap — FaceGuardV2

## 🎯 Product Goal
To develop a reliable, high-speed face recognition access control system deployed on Raspberry Pi 5 hardware, featuring secure local/remote user registration, and comprehensive security auditing.

---

## 🏃‍♂️ Sprint 1: Core Authentication & Emulation Mode
* **Milestone:** [Sprint 1 Milestone Link]()
* **Dates:** June 15, 2026 — June 21, 2026
* **Sprint Goal:** Establish a fully functional local database architecture and visual UI emulation to test the door lock logic without physical hardware access.
* **Expected Outcome:** Developers can register a user locally via mock vectors and visually verify the success/failure state of the servo motor on an x86 platform.

### Planned Items
* 👥 **User Stories:**
  * [US-002] [Issue #12]() — User registration by capturing face vectors.
  * [US-007] [Issue #15]() — UI emulation of the servo motor rotation on x86 laptop.
* ⚙️ **Supporting PBIs:**
  * [PBI] [Issue #16]() — Core Database Schema Design (Profiles & Embeddings table).
  * [PBI] [Issue #17]() — Integrate InsideFace and OpenCV image capture pipeline scripts.

---

## 🏃‍♂️ Sprint 2: Physical Hardware Integration
* **Milestone:** [Sprint 2 Milestone Link]()
* **Dates:** June 22, 2026 — June 28, 2026
* **Sprint Goal:** Migrate the core authentication system from visual emulation to real physical edge execution on Raspberry Pi 5.
* **Expected Outcome:** Approaching the physical camera unlocks the door by physically driving the servo motor connected to the GPIO pins.

### Planned Items
* 👥 **User Stories:**
  * [US-001] [Issue #20]() — Automatic door unlocking upon successful face recognition.
  * [US-006] [Issue #22]() — Physical servo motor rotation and auto-return functionality.
* ⚙️ **Supporting PBIs:**
  * [PBI] [Issue #25]() — Setup GPIO hardware control libraries for Raspberry Pi 5.

---

## 🏃‍♂️ Sprint 3: Security Hardening & Metrics
* **Milestone:** [Sprint 3 Milestone Link]()
* **Dates:** June 29, 2026 — July 05, 2026
* **Sprint Goal:** Minimize system vulnerabilities against photo-spoofing and mathematically optimize the identification threshold using precision/recall curves.
* **Expected Outcome:** The system rejects high-resolution digital screen spoofing attacks and logs comprehensive failure categories for security auditing.

### Planned Items
* 👥 **User Stories:**
  * [US-008] [Issue #30]() — Evaluate face recognition pipeline on real datasets to calculate curves.
  * [US-010] [Issue #32]() — Detailed access attempt logging (confidence, lighting, masks).
  * [US-011] [Issue #35]() — Enforce strict lock state for unknown users or low confidence.