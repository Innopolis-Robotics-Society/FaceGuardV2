# FaceGuardV2 - Week 4 Report

> **For course/internal use.** This is a dated weekly course-assignment report, kept as historical evidence, not customer-facing product documentation. For current product setup and architecture, see the documentation index in the root [README.md](../../README.md).

**FaceGuardV2** is a real-time face-recognition access control system built on Raspberry Pi 5.
The system detects a face, extracts its embedding using InsightFace, compares it against a
registered-user database, and unlocks a physical door via servo motor on successful recognition.
Runs on both Raspberry Pi 5 (ARM) and x86 laptop, with servo visually emulated on x86.

**License:** [MIT License](../../LICENSE)

# Link to the product backlog
[Product backlog](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues)
# Link to the sprint backlog
[Sprint backlog](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/milestone/2)
# Link to the Assignment 4 Sprint milestone
[Sprint milestone](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/milestone/2)
# Sprint Goal, Sprint dates, and short scope summary
**Sprint Dates:** June 22, 2026 – June 28, 2026  
**Sprint Goal:** Successfully deliver, test, and validate **MVP v1.1.0** of the FaceGuardV2 system, ensuring full deployment on target ARM hardware (Raspberry Pi 5), passing all automated QA gates with >30% test coverage, and validating core features through a formal customer demonstration.
**Summary:**  
Raspberry Pi 4 Optimization  
- Model Downsizing: Swapped buffalo_l (330MB, GPU) for buffalo_sc (16MB, CPU) to ensure high performance on the Pi 4 CPU.

- Dependency Cleanup: Stripped out redundant dependencies to minimize container size and RAM overhead.

Key Bug Fixes & Refactoring  
- Async & Streaming: Fixed browser video rendering by adding the missing asyncio import (ml_service) and replaced blocking time.sleep with asyncio.sleep (ml_stub).

- Concurrency: Resolved a critical race condition involving global variables in ml_service.

- Code Quality: Modernized the deprecated @app.on_event("startup") decorator, purged a duplicate /healthz route, and removed dead BackgroundTask code in stream.py.

- API Strictness: Explicitly added the missing Query(...) validation macro to the today parameter in pages.py.
# Total Sprint size in Story Points
16
# Summary of delivered product changes
- Fix bugs in MVP_v1  
- Optimizing product for real deployment in Rsupbery Pi 4 via deleting redundant dependencies and changing model on bufallo_sc instead of model bufallo_l
# Link to the runnable product
[Product](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/tag/v1.1.0)
# Link to current access or run instructions
[Run instruction](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/v1.1.0/README.md#how-to-run)
# Respond to Customer Feedback on the MVP
| Feedback point                                          | Resulting PBI or issue                                                     | Status                      | Response                                                                                                        |
|---------------------------------------------------------|----------------------------------------------------------------------------|-----------------------------|-----------------------------------------------------------------------------------------------------------------|
| The customer wants to see the full functionality of CRUD | [#53](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/53) | Planned for this Sprint     | Add Remove operation from the CRUD                                                                              |
| The customer asked to give temporary access dynamically | [#20](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/20) | Planned for this Sprint     | In the next version it should be possibility to give the constant access and change it to temporary dynamically |
| The customer asked about сheck for liveliness           | [#55](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/55) | Not planned for this Sprint | In the future versions of the product it might be added                                                         |

# Links
[docs/roadmap.md](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/docs/roadmap.md)  
[docs/definition-of-done.md](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/docs/definition-of-done.md)  
[docs/quality-requirements.md](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/docs/quality-requirements.md)  
[docs/quality-requirement-tests.md](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/docs/quality-requirement-tests.md)  
[docs/testing.md](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/docs/testing.md)  
[docs/user-acceptance-tests.md](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/docs/user-acceptance-tests.md)  

# Summary of the quality model used and selected ISO/IEC 25010 sub-characteristics
1. Functional SuitabilityFunctional Correctness (Accuracy): The system must guarantee reliable face recognition. This is continuously verified by evaluating the pipeline on validation datasets to calculate precise precision, recall, and F1-score metrics before setting classification thresholds.  Functional Completeness: The core software must fully execute the automated access loop, which includes registering user faces into the database and triggering physical mechanics upon successful identification.  

2. SecurityAccountability: The application guarantees full auditability by logging every access attempt in a structured database format. These audit logs capture critical metadata, including timestamps, recognition confidence scores, and categorical failures such as poor lighting or presence of masks.  Authenticity & Integrity: System integrity mandates that the door remains securely locked whenever confidence drops below the threshold or the user is unknown. Furthermore, future releases include a liveness detection check to prevent system spoofing via printed photographs.   

3. PortabilityAdaptability & Installability: The system is explicitly designed for cross-platform consistency by being fully packaged into multi-architecture Docker containers. This allows FaceGuardV2 to adapt and run seamlessly across both development/debugging laptops (x86) and target deployment edge units (ARM-based Raspberry Pi 5).  
 
4. MaintainabilityTestability: High testability is achieved by decoupling business logic from target hardware. The system uses a dedicated software abstraction (EmulatedServo) to simulate hardware feedback on non-ARM environments. This enables automated unit and integration tests to safely run in isolated CI environments while maintaining the required test coverage gate (above 30%).  Modularity & Analyzability: The codebase adheres to strict modular design principles, isolating database transactions from ML inferences. This is automatically enforced in the CI pipeline via static code analysis, utilizing tools like Ruff for linting/formatting and Mypy for static type checking to eliminate technical debt.
# Testing status summary, including critical modules and per-module line coverage status
The testing suite ensures the reliability of core application workflows, cryptographic operations, and hardware interface boundaries. All critical system components are enforced by an automated quality gate requiring a minimum of 30% line coverage.

### 1. Critical Modules and Coverage Status
[See testing](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/docs/testing.md)

### 2. Automated Test Suite Execution
The test matrix isolates units, APIs, and non-functional quality requirements down to separate execution targets:

* **Unit Tests:** Run via `pytest -m "not integration and not qrt"` to validate authentication logic, configurations, and isolated servo routines in a clean state. **Status: Passing**.
* **Integration Tests:** Run via `pytest -m integration` utilizing FastAPI's `TestClient` alongside test database transactions to check end-to-end API route logic. **Status: Passing**.
* **Automated Quality Requirement Tests (QRTs):** Run via `pytest -m qrt` to continuously enforce non-functional boundaries from QR-001 to QR-005. **Status: Passing**.

### 3. Pipeline Automated Quality Gates
Every code increment targeting the default protected branch must satisfy the following checks before it can be integrated into a stable release:
* **Linting & Formatting:** Managed via `ruff` and `ruff format --check` to eliminate stylistic syntax issues and guarantee uniform code styling.
* **Static Typing:** Enforced using `mypy` to find structural type errors prior to compilation/execution.
* **Supply Chain Security:** Scanned via `pip-audit` to inspect target package configurations (`pyproject.toml`) against open PyPI vulnerability registers. Upstream warning items (e.g., `jinja2`, `pillow`) are tracked for future dependency bumps.
# Links
**Unit tests:** [unit test 1](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/MVP_v1/tests/test_auth.py), [unit test 2](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/MVP_v1/tests/test_servo.py)  
[Integration tests](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/MVP_v1/tests/test_integration.py)  
[Automated quality requirement tests](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/MVP_v1/tests/test_database.py)  
[CI pipeline](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/.github/workflows/ci.yml)  
[Latest protected-default-branch CI run](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/28328296363)  

# Branch protection
![Photo](images/default-branch-settings.png)

# Report links for linting, coverage, tests, and the additional QA check
[Linting](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/28289144695/job/83818036331)  
[Coverage](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/docs/testing.md)  
[Tests](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/tree/main/MVP_v1/tests)  
[QA](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/actions/runs/28289144695/job/83818036342)
# Influence of tests
1. Process Impact: Enforcing Quality Gates
Branch Protection: Tests act as an automated gatekeeper. Code cannot be merged into the main branch if the CI pipeline fails.
Definition of Done (DoD): Tasks cannot be finalized without proper test coverage, ensuring team alignment on code reliability.
Requirements Compliance: Directly secures and documents the mandatory code coverage threshold (above 30%) required for the submission.
2. Architectural Impact: Better Code Design
Hardware Abstraction: Because the GitHub CI environment lacks access to the physical Raspberry Pi hardware, testing forced the implementation of a software emulator (EmulatedServo). This successfully decoupled the core business logic from the hardware layer.
Environment Isolation: Using isolated database instances for test runs guarantees that the test suite is entirely reproducible and never corrupts live application data.
3. Technical Impact: Regression Prevention
Security Stability: Automated tests ensure that critical components like user authentication and password hashing remain unbroken during future code modifications or optimizations.
Quality Requirements: Automatically verifies non-functional requirements, such as mandatory audit logging for face recognition events and the automated expiration of guest access permissions
# SemVer release
[MVP v1.1.0](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/releases/tag/v1.1.0)
# Link to CHANGELOG.md
[CHANGELOG.md](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/CHANGELOG.md)
# Demo video
[Video](https://drive.google.com/drive/folders/1ZOLlZ0Ua3TId5htnEppaHtL4WZBc0CPA?usp=sharing)
# Presentation
[reports/week4/presentation.pdf](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/tree/main/reports/week4/presentation.pdf) 
# UAT results summary
Based on the MVP demonstration and the feedback table above, the customer acceptance results can be summarized as follows:

Current Sprint Adjustments: The customer approved the core MVP but requested two immediate enhancements. We have successfully prioritized and integrated these into the current sprint: completing the administrative lifecycle with a Remove operation and allowing dynamic switching between constant and temporary access rules.

Future Roadmap: The request for Liveness Detection (anti-spoofing) was recognized as a critical security upgrade and formally moved to the long-term product backlog to avoid disrupting the current deployment deadline.

Status: The MVP v1 has been formally accepted by the customer, subject to the active implementation of the two current sprint items.
# Link to the customer review transcript
[Transcript](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/reports/week4/customer-review-transcript.md)

# Links
[reports/week4/customer-review-summary.md](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/reports/week4/customer-review-summary.md)  
[reports/week4/reflection.md](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/reports/week4/reflection.md)  
[reports/week4/retrospective.md](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/reports/week4/retrospective.md)  
[reports/week4/llm-report.md](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/blob/main/reports/week4/llm-report.md)

# Summary of the current product status
Core Functionality: The core MVP architecture—including user authentication, database management, and servo emulation—is functional and ready for further integration.

CI/CD Pipeline & Code Quality: The automated GitHub Actions pipeline is fully operational and completely green. It successfully runs code style linting and formatting using Ruff, along with static type checking via Mypy.

Testing & Coverage: Automated workflows successfully separate and execute unit tests and quality requirement tests. The overall code coverage meets the project's strict requirement of remaining above the 30% threshold.
# Summary of the next steps
Complete CRUD Capabilities: Implement the missing Remove operation for user and guest profiles to provide full administrative management lifecycle.

Dynamic Access Control: Develop a mechanism allowing administrators to dynamically shift access rules between constant and temporary permissions on the fly.

Maintain Quality Gates: Ensure that the implementation of these new features does not drop the overall test coverage below the required 30% threshold and passes all CI pipeline checks.

Biometric Anti-Spoofing: Initiate research and development for a Liveness Detection check to prevent spoofing attacks (e.g., bypassing the camera using a photo) and fully secure the face recognition module.
# Contribution traceability table
| Member | Contribution                                                                                                 |
|--------|--------------------------------------------------------------------------------------------------------------|
| @Kenzyss | Part 5, 8 assig 4 + part 7. The Product Repository Requirements file contains the part for the 4th assignment |
| @newsow | Fixed all the bugs. Optimized the project for Rasbury pi 4. Made a release                                                                                                             |
| @b3ss0n | Analysed and summarised meeting with the client, formed the contribution of LLM                              |
| @NadezhdaVoskan | Сreated quality requirements, quality requirement test and UAT scenarios                                                                                                             |
| @XeOneD | Part 14, Part 2, filled README file, prepare assignment report on Moodle                                                                                                             |
| @TheShamil | Updated the definition-of-done file according to the requirements, wrote the reflection.md file              |

# Sprint milestone
![Sprint milestone](images/milestone.png)  
![Latest protected-default-branch CI run](images/CI-run.png)  
![Branch protection or rules evidence](images/default-branch-settings.png)  
![Coverage or test report](images/Coverage.png)  
![Additional QA check result](images/QA.png)  
![SemVer release](images/SemVer.png)  
![Example reviewed issue-linked PR/MR](images/PR.png)  
