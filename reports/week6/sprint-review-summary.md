# Project Summary: Sprint 4 Review & Transition Assessment

---

## 1. Planned Sprint 4 Goal & Week 6 Trial Release Evaluation
* **Objective:** The goal for this cycle was to deploy the functional face-recognition and access control system onto the target hardware (Raspberry Pi), verifying live background processes, WebSocket communication, and anti-spoofing validation.
* **Status:** The core backend features are operational. The system successfully processes events via WebSockets in the background while users navigate other pages, and the automated log rotation (15–30 days) and filtering are working. However, an initial connection delay causes the service status to temporarily display as offline.

## 2. Customer Trial & User Acceptance Testing (UAT) Results
During the live trial, the Customer (Speaker 1) identified functional gaps and usability blockers that must be resolved:
* **Pass Management Workflow:** The current approach of issuing passes by a generic "number of days" was rejected. The Customer requires an exact date-picker input where the expiration time can be specified down to the hour and minute.
* **User Interface:** The frontend does not meet acceptance criteria. The interface lacks visual appeal, suffers from poor visibility, uses jarringly high-contrast dark tables, and lacks design consistency with the backend ecosystem.

## 3. Transition-Readiness Findings
The system is **not yet ready for production transition** due to significant performance issues on the Raspberry Pi hardware:
* **Liveness Over-Engineering:** The anti-spoofing mechanism is too slow. While the 1–2 second delay and 3-second blinking window successfully block photo-spoofing, the process frequently fails or causes extreme authentication delays for legitimate users.
* **Frame Rate Issues:** The video stream currently runs at an inadequate rate of approximately 15 frames per second.
* **Software Overhead:** Heavy latency is introduced by unoptimized code, including complex frontend-backend data packets and redundant copying of user embedding arrays in memory.

## 4. Customer-Facing Documentation Review Results
* **Current Assets:** A Static Site Generator (SSG) is already operational on GitHub Pages, successfully documenting the system's architecture and general principles of operation.
* **Gaps Identified:** The documentation lacks proper user onboarding and deployment clarity. The main repository requires a complete cleanup, structured version tags, and a more robust root README.

## 5. Resulting Follow-Up Work for Sprint 5
To prepare the project for final submission and satisfy all customer requirements, Sprint 5 must focus on optimization and refinement:

### Core Optimization & Performance
* **Refactor Liveness:** Streamline the blink-detection algorithm to make user validation significantly faster and eliminate high false-rejection rates.
* **Code Optimization:** Trim transmission packets, eliminate redundant logic, and remove expensive array-copying operations for user embeddings.
* **Maximize Frame Rate:** Optimize the video pipeline to achieve a stable stream of 24 to 30 frames per second on the Raspberry Pi.

### Feature & UI Adjustments
* **Absolute Expiration Dates:** Re-engineer the pass creation feature to support exact calendar dates and specific hour/minute parameters.
* **UI/UX Polish:** Redesign the frontend layout to ensure it is clean, adaptive, visually consistent, and uses a well-balanced color scheme.

### Documentation & Repository Presentation
* **README Update:** Expand the root README to explicitly document main operating conditions and include a clear, step-by-step guide on how to launch the system.
* **Repository Cleanup:** Tidy up the codebase, remove development clutter, apply clear tags, and finalize the GitHub Pages site to ensure the project looks polished and professional.