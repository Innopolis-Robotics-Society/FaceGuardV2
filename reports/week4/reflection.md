# Week 4 Reflection

## Learning points

This Sprint we learned how to translate abstract quality expectations into measurable quality requirements using the ISO/IEC 25010 model. Writing scenarios in the form *When <source> <stimulus> under <environment>, the <artifact> shall <response> within <response measure>* forced us to be concrete about what "fast" or "reliable" means for FaceGuardV2, and to attach each requirement to an automated test that can fail in CI.

We learned that a quality requirement test (QRT) is not the same as a normal unit test. A QRT verifies a measurable non-functional scenario, not implementation correctness. Reusing existing pytest cases as QRTs only worked when the test directly exercised the scenario text; in several cases we had to write new tests with explicit thresholds.

Configuring CI for Assignment 4 showed that the value of a pipeline is not the number of jobs, but whether each job maps to a real risk. Splitting the workflow into lint, format check, unit tests, integration tests, automated QRTs, coverage reporting, and one additional QA check made the failure surface inspectable.

Responding to customer feedback on MVP v1 was harder than expected. Several requests competed with the Sprint quality goal, so we had to triage: address the highest-impact points now, defer the rest to the backlog with a rationale, and record the decision in the feedback response table instead of silently dropping it.

Updating the Definition of Done to require CI gates, automated QRTs, and 30% critical-module coverage changed how the team plans a PBI. "Done" is no longer "the code works on my laptop" but "the code passes every gate on the protected default branch, with preserved evidence."

## Validated assumptions

We confirmed that the FastAPI + SQLite stack under `MVP_v1/` is testable with pytest and pytest-cov. Critical modules (`app/auth.py`, `app/recognition.py`, `app/ml_client.py`, `app/servo.py`, `app/database.py`) can be tested in isolation, and FastAPI routes can be driven end-to-end against a temporary SQLite database.

We confirmed that GitHub Actions is sufficient for the Assignment 4 CI requirements: a single workflow with multiple jobs can run linting, formatting, unit tests, integration tests, QRTs, coverage, and one additional QA check, and surface each result on PRs and on `main`.

We confirmed that the Week 3 Definition of Done was too weak for Assignment 4. It covered acceptance criteria, review, merge, and changelog, but not CI gates, QRTs, or critical-module coverage.

We confirmed that the customer cares about real recognition quality and reliable lock behaviour, not UI polish. This validates the Sprint decision to spend capacity on quality, automation, and CI rather than on new features.

We rejected the assumption that the existing Week 3 tests would automatically satisfy the 30% critical-module coverage gate. Several modules needed additional unit tests, and global coverage is still lower than critical-module coverage because templates, static assets, and ad-hoc scripts are not exercised.

## Friction and gaps

The main difficulty was keeping all Assignment 4 artifacts synchronized. Quality requirements, QRTs, the testing status file, the DoD, the Week 4 public report, and the CI workflow all reference each other; updating one without updating the others produced broken Lychee links and stale evidence pointers.

A second source of friction was the boundary between unit tests, integration tests, and QRTs. Several existing pytest cases blurred the line, and we had to relabel or split them so each QRT maps to exactly one measurable scenario.

Technical risks remain around the real face recognition pipeline. MVP v1 still uses an ML stub; the QRTs we wrote for recognition latency and confidence are valid for the stub, but the real model on Raspberry Pi 5 may violate the response-time threshold.

Coverage gaps persist in non-critical modules: HTML templates, JavaScript, configuration loading, and the `ml_stub` service. These drag global coverage below critical-module coverage. We have explained the gap in the testing documentation per the repository requirements, but the gap itself is not closed.

The public/private evidence split required care. The customer review recording, timecodes, and customer-identifying details had to stay out of the public repository, while the sanitized summary had to be committed.

## Planned response

In the next Sprint, the team will keep every Assignment 4 CI gate active on PRs and on the protected default branch. No gate will be removed, disabled, or narrowed only because the submission is complete. If a product change makes a gate obsolete, it will be replaced with a documented equivalent or stronger check.

The team will close the coverage gap on critical modules by adding targeted unit tests for `app/recognition.py` and `app/ml_client.py`, and integration tests for the FastAPI route plus SQLite persistence boundary.

The team will migrate the ML stub to the real face recognition pipeline on Raspberry Pi 5 and re-run the recognition latency and confidence QRTs against real hardware. If the threshold is violated on the target device, the scenario will be re-scoped with a hardware-appropriate measure and the change will be documented.

The team will address the deferred customer feedback points recorded in the customer feedback response table. The next Sprint Planning will decide which of them enter the Sprint and which stay in the Product Backlog.

The team will keep the DoD and the testing documentation current. Any change to the product stack, critical modules, or CI configuration in a later Sprint will trigger a review of these documents so the gates continue to describe the actual completion standard.

Relevant links:

* Definition of Done: [`docs/definition-of-done.md`](../../docs/definition-of-done.md)
* Quality requirements: [`docs/quality-requirements.md`](../../docs/quality-requirements.md)
* Quality requirement tests: [`docs/quality-requirement-tests.md`](../../docs/quality-requirement-tests.md)
* Testing status: [`docs/testing.md`](../../docs/testing.md)
* User acceptance tests: [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md)
* Roadmap: [`docs/roadmap.md`](../../docs/roadmap.md)
* User-story registry: [`docs/user-stories.md`](../../docs/user-stories.md)
* Changelog: [`CHANGELOG.md`](../../CHANGELOG.md)
* MVP v1 run instructions: [`README.md`](../../README.md)
* MVP v1 implementation folder: [`MVP_v1/`](../../MVP_v1/)
