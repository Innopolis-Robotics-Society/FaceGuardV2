# Definition of Done (DoD)

This document defines the shared minimum completion standard for all Product Backlog Items (PBIs) in the FaceGuardV2 repository. A PBI may be marked `Done` only when both its issue-specific acceptance criteria and this team Definition of Done are satisfied.

## 1. Implementation & Code Quality
- [ ] The code is written, successfully compiles/builds, and addresses the specific requirements of the PBI.
- [ ] The code has been committed to an issue-linked branch following the naming format: `<issue-number>-short-description`.
- [ ] No secrets, passwords, or sensitive data are included in the code.

## 2. Testing & Verification
- [ ] All issue-specific Acceptance Criteria defined in the PBI are satisfied.
- [ ] The changes do not break existing functionality.
- [ ] Verification evidence is preserved in the PR/MR (e.g., screenshots, test output, or logs).

## 3. Review & Workflow Integration
- [ ] A Pull Request (PR/MR) has been created using the extended PR template.
- [ ] The work has been reviewed by at least one other team member (different from the implementer).
# Definition of Done (DoD)

This document defines the shared minimum completion standard for all Product Backlog Items (PBIs) in the FaceGuardV2 repository. A PBI may be marked `Done` only when both its issue-specific acceptance criteria and this team Definition of Done are satisfied.

## 1. Implementation & Code Quality
- [ ] The code is written, successfully compiles/builds, and addresses the specific requirements of the PBI.
- [ ] The code has been committed to an issue-linked branch following the naming format: `<issue-number>-short-description`.
- [ ] No secrets, passwords, or sensitive data are included in the code.

## 2. Testing & Verification
- [ ] All issue-specific Acceptance Criteria defined in the PBI are satisfied.
- [ ] The changes do not break existing functionality.
- [ ] Verification evidence is preserved in the PR/MR (e.g., screenshots, test output, or logs).

## 3. Review & Workflow Integration
- [ ] A Pull Request (PR/MR) has been created using the extended PR template.
- [ ] The work has been reviewed by at least one other team member (different from the implementer).
- [ ] The PR/MR has received explicit approval from the reviewer.
- [ ] For supporting or implementation PBIs, the issue-linked PR/MR is successfully merged into the protected default branch (main).

## 4. Documentation & Traceability
- [ ] The root `CHANGELOG.md` is updated with all user-visible changes, new features, or bug fixes.
- [ ] Relevant documentation (`docs/interface.md`, `README.md`, etc.) is updated if the interface, architecture, or setup instructions have changed.
- [ ] For User Story PBIs: All linked supporting PBIs required to satisfy the story's acceptance criteria are reviewed, merged, verified, and marked `Done`.
