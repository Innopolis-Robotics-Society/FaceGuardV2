# Sprint Retrospective — Sprint 4 (Week 6)

## What went well

- Raspberry Pi 5 hardware deployment was completed within the Sprint window.
  The Docker Compose stack runs on the target device, the servo is wired to
  the documented BCM GPIO pin, and the recognition loop produces verdicts
  against real camera input. The `SERVO_MODE=gpio` path that had only been
  exercised in emulated mode during Sprint 3 now runs against real hardware
  without code changes, which validates the servo abstraction captured in
  `docs/architecture/adr/ADR-004-servo-abstraction-with-emulated-mode.md`.
- A stable Week 6 trial release was shipped as SemVer tag `v2.1.0` on the
  protected default branch, mapped to the Sprint 4 milestone, and linked
  from the customer handover document. The release identifies itself as the
  Week 6 trial or handover-candidate release for Assignment 6 and links to
  the current run instructions in `README.md` and `MVP_v1/README.md`.
- The customer-facing documentation review required by Part 3 of Assignment 6
  was completed with the customer. `README.md`, `docs/customer-handover.md`,
  the access instructions in `MVP_v1/README.md`, and the known-limitations
  section were walked through together. The customer confirmed that the
  entry-point routing in `README.md` is clear and that the handover document
  is sufficient for the reached handover level, with the follow-up items
  captured in the Sprint 5 expected scope.
- Threshold calibration on real hardware produced a working `THRESHOLD`
  value for the `buffalo_sc` model on Raspberry Pi 5. The calibration
  results were recorded in `docs/quality-requirements.md` and
  `docs/quality-requirement-tests.md` so the values are reproducible by
  the customer after transition.
- The Week 6 Sprint Review, customer trial, and transition-readiness
  discussion were covered by a single recorded meeting, which kept the
  private-evidence burden low and made the public summary, transcript,
  and feedback table consistent with each other.

## What did not go well

- The independent SD card recommended by the customer in Sprint 3 took
  longer to source than expected, which pushed the first real-hardware
  deployment attempt to the second half of the Sprint. The team had to
  fall back to `SERVO_MODE=emulated` development for the first two days
  of Sprint 4, which reduced the time available for on-device calibration.
- Threshold calibration on real hardware surfaced a recognition-latency
  regression that was not visible on x86: the `buffalo_sc` model takes
  longer per inference on Raspberry Pi 5 than the Sprint 3 QRT threshold
  allowed. The QRT was re-scoped with a hardware-appropriate measure, but
  the re-scoping consumed capacity that was originally planned for
  documentation polish and for the Active Liveness ADR.
- The Active Liveness ADR planned in the Sprint 3 reflection was drafted
  but not merged during Sprint 4. The draft lives on a feature branch and
  is not yet on the protected default branch, so it cannot be linked from
  `docs/architecture/README.md` or from the security quality requirement
  until Sprint 5. Merging this ADR with a stable ID is recorded as a
  Sprint 5 follow-up item in the Sprint 5 expected scope.
- The Week 6 transition-readiness meeting produced more follow-up items
  than expected. The customer asked for clearer recovery instructions for
  the case where the SD card fails on the device, and for an explicit
  statement of which environment variables the customer must set
  themselves versus which the team pre-configures in `.env.example`.
  These items were converted into PBIs for Sprint 5, but they pushed the
  Sprint 5 scope above the team's original estimate.

## What the team changed or attempted to change based on the previous Sprint Retrospective, and what results they observed

- **Apply a 1.5× buffer during planning for refactoring and infrastructure
  tasks (Sprint 3 action point 1):** Applied to the hardware deployment
  task. The 1.5× buffer absorbed the SD-card sourcing delay without
  forcing the team to drop the trial release scope. Result: the trial
  release still shipped within the Sprint window, but the buffer was
  almost entirely consumed by a single blocking dependency, which
  suggests that 1.5× is the right scale for software refactoring but
  not generous enough for hardware-blocked work.
- **Define integration checkpoints for new pipeline components (Sprint 3
  action point 2):** Applied to the threshold-calibration work and to
  the on-device servo verification. Each pipeline-touching change had a
  mid-Sprint integration check on real hardware. Result: the
  recognition-latency regression was caught at the integration checkpoint
  instead of at the Sprint Review, which gave the team time to re-scope
  the QRT and to record the new threshold in
  `docs/quality-requirement-tests.md` before the customer trial.

## Action points

1. **Treat hardware-blocked tasks as a separate estimation class.**
   Hardware sourcing, GPIO wiring, and on-device calibration now
   consistently exceed even a 1.5× buffer when they chain together. For
   Sprint 5, hardware-dependent PBIs will be estimated at 2× the nominal
   effort and will carry an explicit "blocked by hardware" note in the
   issue body so the team can re-plan early if a hardware dependency
   slips. This is directly relevant to the SD-card failure recovery
   instructions and to the on-device threshold verification that Sprint
   5 inherits from the Week 6 customer trial.
2. **Add a documentation-recovery drill to the handover checklist.**
   The customer's request for clearer SD-card failure recovery
   instructions exposed a gap in `docs/customer-handover.md`. For
   Sprint 5, the team will run a short drill in which one team member
   attempts to recover the system from a simulated SD-card failure
   using only `docs/customer-handover.md` and `README.md`, and any
   step that cannot be completed from the documentation will be added
   to the document before the final transition. The drill output will
   also feed the final transition outcome confirmation required by
   Part 8 of Assignment 6.
