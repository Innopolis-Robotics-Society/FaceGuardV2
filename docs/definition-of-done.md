# Definition of Done (DoD)

This document defines the shared minimum completion standard for all Product Backlog Items (PBIs) in the FaceGuardV2 repository. A PBI may be marked `Done` only when both its issue-specific acceptance criteria **and** every applicable item in this Definition of Done are satisfied.

## 1. Implementation & Code Quality

- [ ] The code is written, successfully compiles/builds, and addresses the specific requirements of the PBI.
- [ ] The code has been committed to an issue-linked branch following the naming format: `<issue-number>-short-description`.
- [ ] Source-code linting passes for the changed code (e.g., `ruff check` for the Python/FastAPI backend under `MVP_v1/`).
- [ ] Formatting or type checking passes where applicable to the changed code (e.g., `ruff format --check`).
- [ ] No secrets, passwords, PII, customer-owned assets, or other sensitive data are included in the code or commit history.

## 2. Testing & Verification

- [ ] All issue-specific Acceptance Criteria defined in the PBI are satisfied and verified before merge.
- [ ] Relevant automated unit tests pass for the changed code (e.g., `pytest` under `MVP_v1/tests/`).
- [ ] Relevant automated integration tests pass for affected component interactions (e.g., FastAPI route + SQLite persistence, servo emulation + recognition pipeline).
- [ ] Relevant automated quality requirement tests pass for any quality requirement touched by the PBI, linked from [`docs/quality-requirement-tests.md`](quality-requirement-tests.md). Quality requirements themselves are defined in [`docs/quality-requirements.md`](quality-requirements.md).
- [ ] Critical modules affected by the PBI maintain at least 30% automated line coverage (e.g., reported via `pytest-cov`), as tracked in [`docs/testing.md`](testing.md). If global repository coverage is lower than critical-module coverage, the gap is explained there.
- [ ] The changes do not break existing functionality (no regressions in the protected-default-branch CI run).
- [ ] Testing evidence is preserved in the PR/MR, CI run, or linked documentation (e.g., CI test report, coverage report, screenshots, logs, or links to the relevant run).

## 3. CI & Quality Gates

- [ ] All required CI checks for the product stack pass on the PR/MR before merge: linting, formatting or type checking, build or testable snapshot creation, automated unit tests, automated integration tests, automated quality requirement tests, line coverage reporting, and the additional QA check configured for Assignment 4.
- [ ] The latest protected-default-branch (`main`) CI run is green at merge time.
- [ ] The Lychee link-checking CI run passes for the changed Markdown files, including any new or updated files under `reports/`.
- [ ] If the PBI changes the product stack, quality requirements, critical modules, or CI configuration, the CI pipeline and [`docs/testing.md`](testing.md) are updated accordingly so the gates continue to describe the current completion standard.

## 4. Review & Workflow Integration

- [ ] A Pull Request (PR/MR) has been created using the extended PR/MR template, including the changelog checklist and acceptance-criteria verification prompts.
- [ ] The work has been reviewed by at least one other team member (different from the implementer).
- [ ] The PR/MR has received explicit approval from the reviewer; the approval is visible in the PR/MR history.
- [ ] For supporting or implementation PBIs, the issue-linked PR/MR is successfully merged into the protected default branch (`main`) using merge commits. Squash and rebase merging remain disabled.
- [ ] Direct pushes to `main` are not used; the only allowed direct push is the initial repository setup commit.

## 5. Documentation & Traceability

- [ ] The root `CHANGELOG.md` is updated with all user-visible changes, new features, or bug fixes, using the appropriate `[Unreleased]` category (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`) following [Keep a Changelog](https://keepachangelog.com/).
- [ ] Relevant documentation (`docs/interface.md`, `docs/roadmap.md`, `docs/user-stories.md`, `README.md`, etc.) is updated if the interface, architecture, setup instructions, or product direction have changed.
- [ ] For User Story PBIs: all linked supporting PBIs required to satisfy the story's acceptance criteria are reviewed, merged, verified, and marked `Done`. Traceability between the user-story ID, linked PBIs, PRs/MRs, and verification evidence is preserved.

## 6. Maintenance of Quality Gates

- [ ] The Assignment 4 CI checks, automated tests, automated quality requirement tests, and coverage gates introduced by this Definition of Done continue to apply to later PBIs. They are not removed, disabled, or narrowed only because the Assignment 4 submission has been completed.
- [ ] Later PBIs do not bypass these gates. If a product change makes a check obsolete, the check is replaced by an equivalent or stronger one and the replacement is documented in [`docs/testing.md`](testing.md) and the relevant PR/MR description.
- [ ] If the product stack, quality requirements, critical modules, or CI configuration change in later Sprints, this Definition of Done and the testing evidence in [`docs/testing.md`](testing.md) are updated so they continue to describe the current completion standard, instead of leaving Assignment 4 gates stale.