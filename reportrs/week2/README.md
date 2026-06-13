# Week 2 Report — FaceGuardV2

## Project Overview

**FaceGuardV2** is a real-time face-recognition access-control system built for Raspberry Pi 5 with a camera module. The system detects a face through a live camera stream, extracts a face embedding using the InsightFace library, compares it against a database of registered users, and makes a binary decision — known or unknown — based on a configurable similarity threshold. On successful recognition, a servo motor rotates to physically unlock the door; on a laptop (x86), the servo is visually emulated in the UI. The entire system is designed for Docker packaging with multi-architecture support (ARM and x86).

- **Root LICENSE:** [`/LICENSE`](../../LICENSE) (MIT License, Copyright (c) 2026 Innopolis Robotics Society)

---

## User Stories

- **User Stories document:** [`reports/week2/user-stories.md`](user-stories.md)

The team defined and validated ten user stories covering the core access-control workflow, registration, temporary visitor access, Docker packaging, GUI feedback, physical servo actuation, cross-platform servo emulation, data-driven threshold selection, liveness detection, and failure-mode audit logging. All stories were reviewed and approved by the customer during the Week 2 meeting without modifications.

---

## Prototype and Interface Artifacts

FaceGuardV2 exposes two interfaces: a **graphical interface** (Live Display — OpenCV window) and a **non-graphical interface** (Admin CLI). The graphical interface is implemented in MVP v0; the Admin CLI is documented for production but not yet implemented.

### Graphical Interface — Live Display (OpenCV Window)

The Live Display is the primary user-facing interface. It streams the real-time camera feed in an OpenCV window and transitions through five visual states: **Locked** (no face detected, red border), **Scanning** (face detected and processing, yellow border), **Recognized** (known user, green border with name and confidence score), **Unknown** (face not in database, orange border with score), and **Error** (camera or model failure, flashing red border). The interface requires no user input — the person simply stands in front of the camera and the system reacts passively.

- **Interactive prototype / implementation:** The MVP v0 executable itself serves as the interactive prototype. It can be downloaded and run to experience all five states of the Live Display. See the MVP v0 section below for download and run instructions.
- **Interface documentation:** [`docs/interface.md`](../../docs/interface.md) — Contains the full specification of both interfaces (Live Display and Admin CLI), including ASCII wireframes, state descriptions, and CLI command reference.

### Non-Graphical Interface — Admin CLI

The Admin CLI is a command-line interface planned for system administrators. It provides commands for user registration (`register`), removal (`remove`), listing active users and guests (`list`), adding temporary guest access (`add-guest`), viewing access logs (`logs`), checking system health (`status`), and updating the recognition threshold at runtime (`threshold`). This interface is fully documented but not implemented in MVP v0.

- **Interactive mock / demonstration:** [`docs/interface.md`](../../docs/interface.md) — Contains the complete CLI specification with example inputs, outputs, and error scenarios that serve as the interactive mock for the Admin CLI.
- **Docs:** [`docs/interface.md`](../../docs/interface.md)

---

## MVP v0

- **MVP v0 Report:** [`reports/week2/mvp-v0-report.md`](mvp-v0-report.md)
- **Deployed artifact / runnable build:** [FaceGuardV2 Release v0.0.0 (Windows executable)](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/tag/v0.0.0) — Download `FaceVerification.zip` from the release assets, unzip, and run `FaceVerification.exe`.
- **Source code:** [`MVP_v0/`](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/tree/Assignment-2/MVP_v0) on the `Assignment-2` branch.
- **Run instructions:** See the [root README](../../README.md) for quick-start steps. In summary: download the Windows executable from GitHub Releases, unzip, and double-click `FaceVerification.exe`. The OpenCV window will open and begin streaming from the default webcam.
- **Public video demonstration:** [Google Drive — MVP v0 Demo](https://drive.google.com/file/d/1ttbY5ay20juh_uStaIQ6FwdaV638wXiO/view?usp=sharing)

### MVP v0 Functionality

MVP v0 demonstrates the core face-recognition pipeline end-to-end:

1. **Face detection** — The system uses InsightFace (`buffalo_l` model) to detect faces in the live camera stream via OpenCV.
2. **Registration mode** — On startup, the system enters registration mode. It captures 5 face embeddings at 0.4-second intervals, averages and normalizes them, and stores the reference embedding in memory.
3. **Verification mode** — After registration, the system switches to verification mode. It captures 5 embeddings from the live feed, averages them, and computes the cosine similarity against the stored reference embedding. If the similarity exceeds the threshold (hard-coded at 0.45), the face is recognized as a match; otherwise, it is labeled as unknown.
4. **Visual feedback** — The OpenCV window displays colored borders and status text: green for match (with name and score), red/orange for unknown, yellow for scanning, and flashing red for errors.

### Current Limitations

- Embeddings are hard-coded in memory — no database or runtime registration persistence.
- No hardware actuation — the servo/LED is not yet integrated; only on-screen text changes provide feedback.
- x86/Windows only — the executable is built for Windows; Raspberry Pi and Linux are untested in MVP v0.
- No persistence — no users database, no logs, no audit trail.
- No liveness detection — photos or screens can spoof the system.
- No Admin CLI — not implemented, only documented.
- No Docker — no containerization or multi-arch build.
- No data-driven threshold — the threshold value (0.45) is hard-coded and not derived from precision/recall evaluation.

---

## PR/MR Template and Reviewed PRs

### Minimal PR Template

- **PR Template:** [`.github/pull_request_template.md`](../../.github/pull_request_template.md)

The template requires the author to provide a summary of changes, testing performed, and a reviewer checklist confirming that existing functionality is not broken and no secrets or passwords are present in the code.

### Reviewed PRs Created During Week 2

All pull requests were created against the `main` branch and merged after review:

| # | Title | Branch | Link |
|---|-------|--------|------|
| 1 | docs: week2-skeleton | `docs/week2-skeleton` → `main` | [PR #1](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/pull/1) |
| 2 | chore: pr-template | `chore/pr-template` → `main` | [PR #2](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/pull/2) |
| 3 | chore: gitignore-and-env-example | `chore/gitignore-and-env-example` → `main` | [PR #3](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/pull/3) |

---

## Lychee Link Checker

### Lychee Configuration

- **Configuration file:** [`lychee.toml`](../../lychee.toml)

The Lychee configuration sets verbose mode to `info`, enables scanning of hidden directories (`hidden = true`), includes verbatim links (`include_verbatim = true`), and defines exclusions for Telegram links and localhost addresses.

### Latest Successful Protected-Default-Branch Run

The Lychee link checker runs on every push and pull request targeting the `main` branch via the GitHub Actions workflow:

- **Workflow definition:** [`.github/workflows/lychee.yml`](../../.github/workflows/lychee.yml)

The workflow checks out the repository, runs Lychee with the project configuration, and is configured with `failIfEmpty: false` so that an empty set of links does not cause a build failure. The latest successful run can be viewed on the [GitHub Actions tab](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/workflows/lychee.yml).

### Excluded Lychee Links and Manual Verification

The following links are excluded from Lychee scanning via the `lychee.toml` configuration:

| Excluded Pattern | Reason for Exclusion | Manual Verification |
|------------------|----------------------|---------------------|
| `https://t.me/.*` | Telegram links can break Lychee's logic due to JavaScript rendering requirements and rate limiting | N/A — no Telegram links are currently present in the repository |
| `http://localhost:.*` | Local addresses are not reachable from GitHub Actions runners | N/A — localhost URLs are development-only and are not intended for external access |
| `http://127.0.0.1:.*` | Same as localhost — local loopback addresses are unreachable from CI | N/A — loopback URLs are development-only and are not intended for external access |

**Confirmation:** All excluded link patterns have been reviewed. The Telegram pattern is a precautionary exclusion for potential future links. The localhost/loopback patterns exclude development-only addresses that are intentionally unreachable from CI environments. No currently existing links in the repository match these exclusion patterns, so no manual browser verification was necessary.

---

## Screenshots

Screenshots are stored in [`reports/week2/images/`](images/) and referenced below.

### Protected Default Branch Settings

![Protected default branch settings](images/protected-branch.png)

*The `main` branch is protected on GitHub, requiring pull request reviews before merging. Branch protection ensures that no direct pushes are allowed and all changes must go through reviewed PRs.*

### Example Reviewed PR/MR

![Example reviewed PR](images/reviewed-pr.png)

*Screenshot of a pull request reviewed by a team member (not a self-review). PRs are reviewed against the checklist defined in [`.github/pull_request_template.md`](../../.github/pull_request_template.md).*

### Prototype and Interface Artifacts

#### Live Display — Recognized State

![Recognized state — Live Display](images/recognized-state.png)

*The OpenCV window showing a green border and "MATCH" status when a registered user's face is recognized, with the cosine similarity score displayed.*

#### Live Display — Unknown State

![Unknown state — Live Display](images/unknown-state.png)

*The OpenCV window showing an orange/red border and "UNKNOWN" status when the detected face does not match the registered embedding.*

### Deployed MVP v0 / Runnable Artifact

![MVP v0 running](images/mvp-v0-running.png)

*The MVP v0 Windows executable running and displaying the OpenCV face verification window. The executable is available from [GitHub Releases](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/tag/v0.0.0).*

---

## Coverage

### Stable IDs Covered by the Prototype

The prototype (MVP v0) and interface artifacts represent the following stable user-story IDs:

| Stable ID | User Story | Prototype Coverage |
|-----------|------------|---------------------|
| **US-01** | Automatic Door Unlocking | Partially covered — real-time face recognition pipeline is functional (detection → embedding → comparison → decision), but the hardware servo signal is not yet integrated. The system correctly identifies known vs. unknown faces in the UI. |
| **US-02** | User Registration | Partially covered — the MVP v0 registration flow captures 5 face embeddings and computes an averaged normalized reference embedding. However, this is in-memory only (no persistent database), and there is no admin UI for managing registrations. |
| **US-05** | Graphical User Interface Feedback | Partially covered — the OpenCV Live Display shows real-time camera feed, recognition status (name or "Unknown"), and the cosine similarity score. The interface matches the state machine documented in [`docs/interface.md`](../../docs/interface.md). |
| **US-07** | Cross-Platform Servo Emulation | Foundation laid — the MVP v0 runs on x86/Windows and provides visual feedback (colored borders, text overlays) in place of physical servo actuation. The abstraction layer for swapping GUI-based servo emulation with GPIO on ARM is not yet implemented. |
| **US-08** | Data-Driven Threshold Selection | Foundation laid — the verification pipeline computes cosine similarity and compares against a threshold (currently hard-coded at 0.45). The infrastructure for threshold-based decisions is in place, but no precision/recall evaluation on a labeled dataset has been performed yet. |

### Interface Artifacts and Represented User Stories

- **Live Display (Graphical Interface):** Implemented in MVP v0 and documented in [`docs/interface.md`](../../docs/interface.md). Represents **US-01** (visual access decision feedback), **US-05** (GUI showing name, status, and confidence), and **US-07** (x86 visual servo emulation). The five-state visual system (Locked → Scanning → Recognized → Unknown → Error) directly maps to the real-time recognition workflow.

- **Admin CLI (Non-Graphical Interface):** Documented in [`docs/interface.md`](../../docs/interface.md) with full command specifications, example inputs/outputs, and error scenarios. Represents **US-02** (registration via `register` command), **US-03** (temporary visitor access via `add-guest`), **US-08** (runtime threshold adjustment via `threshold`), and **US-10** (audit logging via `logs`). Not yet implemented.

### MVP v0 Foundation

- **MVP v0 Report:** [`reports/week2/mvp-v0-report.md`](mvp-v0-report.md)

MVP v0 establishes the foundational face-recognition pipeline — from camera capture through detection, embedding extraction, similarity comparison, and visual decision output. This foundation directly supports the following user stories:

| User Story | How MVP v0 Provides Foundation |
|------------|-------------------------------|
| **US-01** Automatic Door Unlocking | The core recognition pipeline (detect → embed → compare → decide) is functional and runs in real time. Only the GPIO hardware signal remains to be connected. |
| **US-02** User Registration | The registration flow captures multiple face angles, averages the embeddings, and stores a reference vector. The pattern is established; persistence (database) and admin flow are the missing pieces. |
| **US-05** GUI Feedback | The OpenCV window renders the camera feed with colored borders, status text, and confidence scores — fulfilling the basic GUI feedback requirements. |
| **US-06** Physical Lock Servo Feedback | Although GPIO servo control is not yet integrated, the visual "UNLOCKED" banner in the UI demonstrates the trigger logic that will eventually drive the physical servo. |
| **US-07** Cross-Platform Servo Emulation | The MVP v0 runs on x86 and provides visual feedback as a stand-in for physical actuation, establishing the dual-platform pattern. |
| **US-08** Data-Driven Threshold Selection | The threshold-based decision logic is implemented (cosine similarity > 0.45 → match). The evaluation framework for data-driven threshold selection is the next step. |

The repeatable smoke-check scenario for MVP v0 is documented in the [MVP v0 Report](mvp-v0-report.md): download the Windows executable, run it, observe the OpenCV window transitioning through registration and verification states as described in the [video demonstration](https://drive.google.com/file/d/1ttbY5ay20juh_uStaIQ6FwdaV638wXiO/view?usp=sharing).

---

## Customer Transcript

- **Full transcript:** [`reports/week2/customer-meeting-transcript.md`](customer-meeting-transcript.md)

The transcript records the complete conversation between the team (Dmitry, Egor, Nadezhda) and the customer. Topics covered include temporary access configuration, liveness detection requirements, LED feedback indicators, lighting conditions, handling of repeated failed attempts, multi-person scenarios, camera placement, and MVP v0 scope definition. All user stories were reviewed and approved by the customer during this meeting.

---

## Customer Meeting Summary

- **Meeting summary:** [`reports/week2/customer-meeting-summary.md`](customer-meeting-summary.md)

The summary distills the customer meeting into structured sections: requirements clarification (temporary access, liveness detection, LED indicators, lighting, failed attempts, multi-person handling, camera placement), MVP scope definition, MVP v0 clarification, user stories review, and action items. The customer approved all functional requirements, the MVP scope, the prototype approach, and all proposed user stories.

---

## Week 2 Analysis

- **Analysis document:** [`reports/week2/analysis.md`](analysis.md)

---

## LLM Report

- **LLM usage report:** [`reports/week2/llm-report.md`](llm-report.md)

The LLM report documents all areas where AI/LLM tools were used during the assignment: coding templates and architecture, CI/CD pipeline development (GitHub Actions / Lychee), GitHub workflow guidance, process documentation, and transcription of meeting recordings. All AI-generated configurations, templates, and text were reviewed, adjusted, and manually verified before integration into the main repository branch.
