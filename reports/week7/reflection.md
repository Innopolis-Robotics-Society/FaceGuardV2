# Week 7 Reflection

## Learning points

Follow-up maintenance taught us that customer feedback from a trial release can be addressed as a set of focused, parallel PRs rather than a single large refactor. The Week 6 Sprint Review produced six feedback points (pass management, backend overhead, video FPS, UI design, repository health, and documentation). In Week 7 the team shipped five merged PRs (#121, #122, #124, #126, #128) that closed five of the six points. Splitting the work by layer (frontend, backend, ML service, docs) let each branch pass the full CI gate independently and reduced integration risk on the protected default branch.

The frontend redesign (PR #128) was the most visible change. The `custom.css` file was restructured into a cohesive, adaptive stylesheet with consistent color tokens and readable table styling. Templates (`dashboard.html`, `users.html`, `user_detail.html`, `register.html`, `login.html`, `logs.html`) were updated for visual hierarchy and mobile responsiveness. The customer’s complaint about “jarringly high-contrast dark tables” was resolved by replacing raw table layouts with styled card-based components and improved spacing.

Backend cleanup (PR #124) eliminated redundant embedding-array copies and trimmed the packet structure between the frontend and the recognition loop. `database.py` was refactored for cleaner CRUD boundaries, `routes/users.py` gained stricter validation, and `recognition.py` was restructured to reduce blocking work in the async loop. The performance overhead flagged in Week 6 dropped measurably in local profiling.

The ML service optimization (PR #126) replaced the active eye-blink challenge with a passive, faster liveness model and fixed the blink-counter regression that caused false rejections on Raspberry Pi. `ml_service/main.py` was restructured to run background inference in a dedicated thread, and the Dockerfile was slimmed. The video pipeline now sustains ~24 FPS on Raspberry Pi 4, which satisfies the customer’s 24–30 FPS request.

Final transition work included updating the UAT execution results (PR #121) to cover the post-optimization verification run, expanding the root README with deployment and operating-condition sections (PR #122), and ensuring the customer-handover document still described the correct setup paths after the Week 7 merges. The transition-readiness checklist from Week 6 was walked through again after the merges; no new blockers were discovered.

The course assignment refers to the final delivered increment as **MVP v3**; in the repository this state is represented by the merged follow-up changes on `main` after tag `v2.1.0`, comprising the frontend redesign, backend cleanup, ML service optimization, and documentation updates.

## Validated assumptions

We confirmed that the servo abstraction (ADR-004) survives both backend refactoring and frontend redesign. The `gpio`/`emulated` toggle and the `SERVO_PIN` configuration required zero changes across the Week 7 PRs.

We confirmed that the `buffalo_sc` model plus the passive liveness check is a viable CPU-only pipeline on Raspberry Pi 4. Recognition latency and FPS stay within the re-scoped QRT thresholds after the background-process optimization.

We confirmed that the customer’s Week 6 priorities were correct: the feedback table mapped cleanly to maintenance PBIs, and resolving the top three complaints (FPS, UI, backend overhead) produced a stable, usable product without adding new user stories.

We confirmed that the full CI gate (ruff, mypy, pytest, integration tests, QRTs, coverage, `pip-audit`, Lychee) scales to rapid follow-up PRs. Every Week 7 branch passed the gate before merge, which prevented regressions from entering `main` while the team was under deadline pressure.

## Friction and gaps

The absolute date-picker with hour/minute precision for temporary access, requested by the customer in Week 6, was not implemented in Week 7. The pass-creation workflow still uses a duration-based selector. This gap is recorded in the product backlog as a post-course improvement; it does not block the current handover because the existing expiry mechanism works for short-term trials.

The Active Liveness ADR planned in Sprint 3 and deferred in Sprint 4 was still not merged by the end of Week 7. The draft exists on a feature branch. The architecture documentation therefore describes the liveness mechanism in the UAT and changelog but not in a dedicated ADR. This is a minor documentation gap that does not affect the runnable product.

No new SemVer tag was cut after `v2.1.0` for the final Week 7 increment. The follow-up changes are merged to `main` and constitute the final delivered state, but the release page still points to `v2.1.0`. Tagging a `v2.2.0` or `v3.0.0` release would make the final delivery artifact unambiguous for the customer.

## Planned response

No further Sprints are planned. The product is in the final transition state described in `docs/customer-handover.md`. The repository, documentation, Docker Compose stack, and hardware wiring guide are prepared for customer inspection and independent use.

The team will update `docs/customer-handover.md` with the final customer confirmation status once the customer completes their independent verification on Raspberry Pi.

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
* MVP v1 run instructions: [`README.md`](../../README.md)
