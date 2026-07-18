# Project Summary: Sprint 5 Review & Final Transition Assessment

---

## 1. Planned Sprint 5 Goal & Delivered MVP v3 Status

* **Objective:** Sprint 5 was planned to close out the Week 6 customer feedback (frame rate, liveness responsiveness, UI/UX, backend overhead, documentation, repository cleanup), tune the recognition threshold on real hardware, and prepare the final `MVP v3` handover.
* **Status:** The frontend redesign, Raspberry Pi performance optimization, and a new LED status-indicator feature (yellow = liveness check, blue = access granted, red = access denied) were implemented and merged during the Sprint. `CHANGELOG.md` and the final `MVP v3` SemVer release are still pending as of this review — see Part 7 for release status.

## 2. Customer Trial & Live Demo Results

During the live trial on the Raspberry Pi deployment, the Customer (Speaker 1) observed and interacted with the running system:
* Confirmed the LED status indicators correctly reflect liveness check, access-granted, and access-denied states.
* Confirmed the recognition loop keeps running in the background even while the browser is on a different tab.
* Confirmed the audit log now only records a new entry on a state transition, instead of repeating identical `denied` entries for a person standing in front of the camera — matching the Week 6 request to reduce log noise.
* Noted that the recognition confidence score observed during the trial was low, ahead of the threshold tuning completed later in the Sprint.
* Confirmed overall satisfaction with the current state of the project.

## 3. Resolved and Unresolved Follow-Up Issues from Week 6

| Week 6 follow-up item | Status |
| --- | --- |
| Frame rate (target 24-30 FPS) | Improved; confirmed on Raspberry Pi. |
| UI/UX redesign (color consistency, readable tables) | Redesigned frontend merged during Sprint 5. |
| Audit-log noise reduction | Confirmed working as intended during the live trial (state-transition-only logging). |
| Backend overhead (redundant embedding copies, packet size) | Optimized. |
| Absolute date/time pass expiration | Confirmed. |
| Recognition threshold tuning | **Done.** |
| Repository cleanup, tags, README | In progress as part of the Week 7 documentation and repository-polish work (Part 3). |

## 4. Final Transition Status and Usefulness

* **Handover level reached:** `Independently used by customer` — the Customer interacted with the running trial directly during the Week 7 session, beyond only watching a team-led walkthrough.
* **Customer-confirmation status:** `Accepted` — the Customer confirmed satisfaction with the project and accepted `docs/customer-handover.md` as sufficient for the reached handover level.
* The product is deployed and running on the Raspberry Pi used for the trial; the Customer did not raise blocking concerns during this session.

## 5. Customer Use, Deployment, and Operational Status

* The trial was run on the team's Raspberry Pi deployment, with the Customer actively exercising the live dashboard, LED indicators, and audit log during the session.
* Deployment on customer-owned infrastructure (i.e., the physical lab door) was not part of this session and remains a post-course consideration.

## 6. Remaining Risks and Post-Course Limitations

* As with `MVP v2`, this remains a course MVP and not a certified physical security system; recognition quality still depends on lighting, camera placement, and the tuned threshold.
