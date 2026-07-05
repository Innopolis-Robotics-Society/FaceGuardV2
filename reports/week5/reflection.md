# Week 5 Reflection

## Learning points

This Sprint the team learned that "documenting the architecture" is not the same as "drawing a diagram after the code is done." Splitting the maintained architecture artifact into a static view, a dynamic view, and a deployment view forced us to reason about FaceGuardV2 from three different angles at the same time: what it is made of, how the important flows move through it, and how it is actually run on a device. Writing each view in PlantUML and committing the `.puml` source next to the rendered `.png` made the diagrams feel like real repository artifacts instead of disposable slides — when the data layer was refactored during Sprint 3, we updated the component diagram in the same PR instead of leaving it stale.

Recording ADRs was the second big learning step. ADR-001 (separate backend and ML service), ADR-002 (SQLite through `FaceDatabase` DAL), ADR-003 (session auth with password hashing), and ADR-004 (servo abstraction with emulated mode) already existed as implicit decisions in the code, but writing them in a consistent Context / Decision / Consequences / Related views structure exposed the tradeoffs we had accepted without naming them. Linking each ADR to its quality requirements in `docs/quality-requirements.md` and to the diagrams in `docs/architecture/README.md` made the traceability two-way: a reader can start from a QR, find the ADR that addresses it, and then find the view that visualizes it.

Refining the development process in `docs/development-process.md` taught us that a workflow document is most useful when it describes what the team actually does, not what a textbook says it should do. The Mermaid `gitGraph` diagram reflects real branch names (`58-fix-the-mvp-v1`, `65-optimizing-product`, `LLM-report`, `presentation`) and real PR numbers (`PR #64`, `PR #66`, `PR #73`), which makes the document readable as evidence rather than as theory. Writing the configuration-management section also forced us to be honest about what counts as a secret and what does not, and to align the `.env` / `.env.example` split with the `.gitignore` rules.

Managing configuration for `MVP v2` showed us that environment-driven configuration is only useful when it is documented in one place. `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `THRESHOLD`, `ML_SERVICE_URL`, `SERVO_MODE`, and `SERVO_PIN` are all listed in `docs/development-process.md` and in the root `README.md`, so a reviewer or a new team member does not have to read `app/config.py` to learn what to set. The customer also confirmed that this matters in practice — they asked about threshold tuning during the Sprint Review, and we could point at the documented variable instead of guessing.

Delivering `MVP v2` taught us that a maintainable increment is more valuable than a large increment. The Sprint 3 scope unified users and guests into a single table with a `type` field, added full CRUD on users and audit logs, implemented active liveness detection based on eye blinking, switched the recognition model to `buffalo_sc` for CPU-friendly inference, and added audit-log rotation. Each of these changes was tied to a tracked issue and a reviewed PR, and each one is reflected in `CHANGELOG.md` under `v2.0.0`. The increment is smaller in new feature surface than MVP v1, but the product is now safer against photo-spoofing, easier to maintain, and ready for hardware deployment.

Reviewing the increment with the customer changed how we prioritize the next Sprint. The customer explicitly said that protection against photos is "completely sufficient for the current scope" and that video anti-spoofing is a bonus, not a requirement. That feedback lets us move motion-control liveness to the backlog and prioritize Raspberry Pi deployment, threshold calibration on real hardware, and the final project defense instead.

## Validated assumptions

We confirmed that three architectural views are sufficient to reason about FaceGuardV2 for the current MVP scope. The component diagram shows the static structure, the registration sequence diagram shows the most cross-component workflow, and the deployment diagram shows the Docker Compose runtime plus the Raspberry Pi hardware boundary. No additional views were needed for Assignment 5.

We confirmed that PlantUML is a practical diagrams-as-code tool for this team. The `.puml` sources are short, diff cleanly in PRs, and render to `.png` files that GitHub displays inline. The render command is documented in `docs/architecture/README.md`, so a reviewer can regenerate any diagram locally.

We confirmed that the four ADRs (ADR-001 through ADR-004) capture the decisions that actually matter at this stage. Each one is linked to at least one Assignment 4 quality requirement, and each one is visible in at least one architectural view. The ADR set is intentionally small: it records decisions that were load-bearing for `MVP v2`, not every minor choice.

We confirmed that the issue-linked feature-branch workflow described in `docs/development-process.md` matches the real repository history. The PRs referenced in the `gitGraph` diagram (`PR #64`, `PR #66`, `PR #69`, `PR #70`, `PR #72`, `PR #73`, `PR #74`, `PR #75`) correspond to merged branches on `main`, and the transition from descriptive branch names to issue-numbered branch names is visible in the same diagram.

We confirmed that the configuration-management rules work for both local development and Raspberry Pi deployment. The `.env.example` files are sanitized, the real `.env` files are ignored, and `SERVO_MODE=emulated` lets the same backend run on a laptop without GPIO hardware. The customer review did not surface any configuration gap that blocked product use.

We confirmed that the customer values real recognition quality and reliable hardware behavior over additional web features. This validates the Sprint 3 decision to spend capacity on liveness detection, CRUD hardening, and model downsizing instead of new dashboard pages.

We rejected the assumption that the existing ADR set would automatically cover liveness detection. The liveness check is currently described in the customer review summary and the changelog, but it is not yet backed by a dedicated ADR. This is recorded as a follow-up in the planned response below.

## Friction and gaps

The main difficulty was keeping the architecture documentation, ADRs, quality requirements, and weekly report synchronized. A change in `docs/architecture/README.md` often implied an update in `docs/quality-requirements.md` (to link the ADR), in the relevant ADR (to link the views), and in `reports/week5/README.md` (to link the new artifact). Doing these updates in the same PR required discipline; doing them across PRs produced short-lived broken Lychee links.

A second source of friction was the boundary between the dynamic view and the static view. The registration sequence crosses the same components shown in the static diagram, so it was tempting to duplicate explanations. We resolved this by keeping the static view focused on structure and coupling, and the dynamic view focused on the order and failure paths of one specific flow.

Technical risks remain around the real face recognition pipeline. `MVP v2` still runs the liveness check and recognition loop against an ML service that has not yet been exercised on Raspberry Pi hardware. The QRTs for recognition latency and confidence are valid for the current `buffalo_sc` model on x86, but the same thresholds may need re-tuning on the target device. Hardware deployment is scheduled for the next Sprint.

Coverage gaps persist in non-critical modules: HTML templates, JavaScript, and the `ml_stub` service are not exercised by automated tests. The gap is documented in `docs/testing.md` per the repository requirements, but the gap itself is not closed. Audit-log rotation (`purge_old_logs(days=30)`) is unit-tested, but the daily background loop that triggers it is only verified manually.

The public/private evidence split required care again. The Sprint Review recording, the UAT recording, the customer's name, and the exact private timecodes had to stay out of the public repository, while the sanitized summary, transcript, and feedback table had to be committed. We used `reports/week5/customer_feedback.md` for the public feedback response table and submitted the private recording link only through Moodle.

The architecture decision to use SQLite (ADR-002) is starting to show its limits. The unified users table introduced in `MVP v2` already required an automatic migration path for legacy two-table databases, and future multi-admin or multi-device deployments may need a separate database server. This is recorded as a tradeoff in ADR-002, not as a defect.

## Planned response

In the next Sprint, the team will deploy `MVP v2` on Raspberry Pi and re-run the recognition latency and confidence QRTs against real hardware. If a threshold is violated on the target device, the scenario will be re-scoped with a hardware-appropriate measure and the change will be documented in `docs/quality-requirements.md` and `docs/quality-requirement-tests.md`.

The team will keep every Assignment 4 and Assignment 5 CI gate active on PRs and on the protected default branch. No gate will be removed, disabled, or narrowed only because the submission is complete. If a product change makes a gate obsolete, it will be replaced with a documented equivalent or stronger check, and `docs/testing.md` will be updated in the same PR.

The team will add a dedicated ADR for the active liveness detection mechanism (eye-blink challenge with randomized timer) so that the security rationale and the residual video-bypass risk are recorded in the same place as the other architecture decisions. The new ADR will be linked from `docs/architecture/README.md` and from the relevant quality requirement once a QRT for liveness is added.

The team will keep the architecture documentation, ADRs, development-process documentation, and configuration-management documentation current. Any change to the product scope, deployment model, service boundaries, quality requirements, or CI configuration in a later Sprint will trigger a review of these documents so they continue to describe the actual system.

The team will continue using the issue-linked feature-branch workflow described in `docs/development-process.md`. New branches will use the `<issue-number>-short-description` naming rule, and new user-visible changes will update `CHANGELOG.md` before merge.

Relevant links:

* Architecture documentation: [`docs/architecture/README.md`](../../docs/architecture/README.md)
* ADR directory: [`docs/architecture/adr/`](../../docs/architecture/adr/)
* Development process and configuration management: [`docs/development-process.md`](../../docs/development-process.md)
* Definition of Done: [`docs/definition-of-done.md`](../../docs/definition-of-done.md)
* Testing status: [`docs/testing.md`](../../docs/testing.md)
* Quality requirements: [`docs/quality-requirements.md`](../../docs/quality-requirements.md)
* Quality requirement tests: [`docs/quality-requirement-tests.md`](../../docs/quality-requirement-tests.md)
* User acceptance tests: [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md)
* Roadmap: [`docs/roadmap.md`](../../docs/roadmap.md)
* Changelog: [`CHANGELOG.md`](../../CHANGELOG.md)
* MVP v2 run instructions: [`README.md`](../../README.md)
* Sprint 3 retrospective: [`reports/week5/retrospective.md`](retrospective.md)
* Sprint Review summary: [`reports/week5/sprint-review-summary.md`](sprint-review-summary.md)
* Customer feedback response table: [`reports/week5/customer_feedback.md`](customer_feedback.md)
