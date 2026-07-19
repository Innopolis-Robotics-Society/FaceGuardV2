# Sprint Retrospective — Sprint 5 (Week 7)

## What went well

- The Week 7 customer trial confirmed that the customer directly interacted
  with the live dashboard, the LED status indicators, and the audit log
  during the session, instead of only watching a team-led walkthrough. This
  moved the handover level from `Trial release available to customer` (Sprint 4)
  to `Independently used by customer`, which is the level recorded in
  [`docs/customer-handover.md`](../../docs/customer-handover.md). The
  customer also explicitly accepted the handover document as sufficient for
  this level, which closes the transition-confirmation work required by
  Part 8 of Assignment 6 without leaving any customer-side blocker open.
- The Sprint 5 follow-up scope inherited from the Week 6 customer meeting
  was largely closed on real hardware. The frontend redesign
  (`CHANGELOG.md` `[Unreleased]` → *Changed* → "Redesigned the admin UI"),
  the LED status-indicator feature (`MVP_v1/app/leds.py`, `LED_MODE=gpio` on
  Raspberry Pi), the audit-log state-transition-only logging, the backend
  overhead reduction, and the absolute date/time pass expiration were all
  merged during the Sprint and observed working during the live trial. The
  Sprint Review summary records each of these as resolved in the
  "Resolved and Unresolved Follow-Up Issues from Week 6" table.
- The Raspberry Pi frame-rate follow-up from Week 6 was closed. The Sprint
  Review transcript records the customer observing inference running at
  "around 20 to 24 FPS" on the Raspberry Pi deployment, which is inside the
  24 FPS lower bound of the 24–30 FPS target set in the Week 6 customer
  meeting. This was achieved without changing the `buffalo_sc` model and
  without disabling the liveness check, which preserves the security
  posture agreed with the customer in Sprint 3.
- Repository ownership transfer to the customer was completed during the
  Sprint, as recorded in [`docs/customer-handover.md`](../../docs/customer-handover.md)
  §2 ("Ownership transfer | Completed"). This is a concrete, inspectable
  transition step that goes beyond documentation updates and is one of the
  reasons the Part 8 transition-confirmation session could be recorded as
  `Accepted` rather than as a follow-up item.
- The recognition-threshold tuning that was deferred from Sprint 4 was
  completed on real trial data. The Sprint Review summary lists
  "Recognition threshold tuning" as `Done`, and the resulting threshold
  value is recorded in [`docs/quality-requirements.md`](../../docs/quality-requirements.md)
  and [`docs/quality-requirement-tests.md`](../../docs/quality-requirement-tests.md),
  so the customer can reproduce the verification after transition without
  depending on team-side knowledge.

## What did not go well

- The final `MVP v3` SemVer release and the corresponding `CHANGELOG.md`
  entry were still pending at the time of the Sprint Review. The Sprint
  Review summary explicitly flags this in §1: "`CHANGELOG.md` and the
  final `MVP v3` SemVer release are still pending as of this review — see
  Part 7 for release status." This means the Sprint closed with code
  merged to the default branch but without the customer-facing release
  artifact that the trial level actually depends on, which weakens the
  traceability between the merged PRs and the delivered MVP version.
- The public sanitized demo video required by Part 14 of Assignment 6 was
  not recorded during Sprint 5. The Week 7 README Part 8 section records
  this explicitly: "The public sanitized demo video is expected to be
  recorded shortly but has not been recorded as of this review." This is a
  Sprint 5 deliverable that slipped past the Sprint Review, leaving
  post-Sprint work for Demo Day preparation.
- Repository cleanup (root `README.md` expansion, removal of development
  clutter, structured version tags on the GitHub Pages site) was still in
  progress at the Sprint Review. The Sprint Review summary lists
  "Repository cleanup, tags, README" as `In progress` rather than `Done`,
  and the Week 7 README Part 8 section repeats this as a remaining
  team-side follow-up. The customer-facing impression of the public
  repository therefore does not yet match the polish level of the running
  product.
- The recognition-confidence score observed by the customer during the
  live trial was low. The Sprint Review transcript records the customer
  saying "The confidence score is quite low, but let's deal with that
  later" and "Overall, I'm satisfied with the project as it stands", so
  this did not block acceptance — but the threshold tuning that followed
  the trial was reactive rather than planned, and the team only
  remembered the task during the trial itself. The transcript records the
  cause directly: "Picking the final threshold value still hasn't been
  done. I worked with the Raspberry Pi setup before and forgot about this
  task."

## What the team changed or attempted to change based on the previous Sprint Retrospective, and what results they observed

- **Treat hardware-blocked tasks as a separate estimation class
  (Sprint 4 action point 1):** Applied to the threshold-tuning PBI and to
  the on-device frame-rate optimization PBI. Both PBIs were estimated at
  2× the nominal effort and labelled as hardware-blocked in the issue
  body, as the action point required. Result: the frame-rate optimization
  absorbed the buffer cleanly and landed inside the Sprint window.
  However, the threshold-tuning PBI still slipped until the Sprint Review
  itself, because the "blocked by hardware" label made the PBI visible as
  a hard-dependency item but did not make it visible as a *forgotten* item
  on the daily board. The 2× buffer was the right scale for the work
  itself, but the action point did not address issue-tracking discipline,
  which is where the actual failure happened.
- **Add a documentation-recovery drill to the handover checklist
  (Sprint 4 action point 2):** Ran the drill. One team member attempted to
  recover the system from a simulated SD-card failure using only
  [`docs/customer-handover.md`](../../docs/customer-handover.md) and
  [`README.md`](../../README.md). Result: the drill surfaced several
  recovery steps that were under-specified in the handover document,
  including the exact `docker compose` command sequence and the
  environment-variable expectations on a fresh SD card. These were added
  to [`docs/customer-handover.md`](../../docs/customer-handover.md) and
  cross-referenced from [`docs/deployment-raspberry-pi.md`](../../docs/deployment-raspberry-pi.md)
  before the Week 7 transition-confirmation session. The drill output also
  fed the final transition outcome confirmation recorded in the Week 7
  README Part 8 section, which is the use case the Sprint 4 retrospective
  predicted. The customer's `Accepted` confirmation during Week 7 is
  direct evidence that the documentation-recovery drill closed the gap it
  was designed to close.

## Action points

1. **Tighten release-finalization discipline.** The Sprint 5 review closed
   with code merged to the default branch but without the final `MVP v3`
   SemVer tag or the matching `CHANGELOG.md` entry. For any future
   release-bearing Sprint (including a hypothetical post-course Sprint or
   a Demo-Day release), the final SemVer tag and the `CHANGELOG.md`
   update must land in the same PR that merges the last Sprint feature,
   not as a follow-up. The team will adopt a release-checklist PR
   template that blocks merge until the tag, the `CHANGELOG.md` entry,
   and the GitHub Release artifact are all confirmed, and the same
   checklist will be applied to close out the pending `MVP v3` release
   during Demo Day preparation.
2. **Front-load Demo Day deliverables at Sprint planning.** The public
   sanitized demo video and the presentation rehearsal were both still
   open at the Sprint 5 review, which left post-Sprint work for Demo Day.
   For any future Sprint that ends in a public presentation, the demo
   video recording, the slide deck, and at least one timed rehearsal
   will be planned as first-class Sprint PBIs with their own story points
   and acceptance criteria, rather than as follow-up tasks after the
   Sprint Review. This is the direct cause of the demo-video slippage
   recorded in the Week 7 README Part 8 section and is the most likely
   slippage risk for the remaining Demo Day work.
