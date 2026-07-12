# LLM Usage in FaceGuard Project — Assignment 6

During Sprint 4 (Assignment 6), Large Language Models (LLMs) were utilized for the following tasks:

1. **Log Analysis on Raspberry Pi:** Analysed runtime logs from the trial deployment to identify the root cause of the silent liveness-detection failure. LLMs helped correlate frame timestamps, inference latency, and the blink-challenge timer to pinpoint the mismatch between camera FPS and detection-window constants.

2. **Liveness Detection Bug Fixes:** Assisted in debugging and patching the eye-blink challenge logic for the Raspberry Pi camera stream. LLMs suggested adjustments to the frame-sampling window, the timer randomisation range, and the fallback behaviour when the stream drops below a minimum FPS threshold.

3. **Backend Optimisation Guidance:** Reviewed profiling output for the CRUD layer and the recognition loop. LLMs proposed index hints for the SQLite `users` table, suggested async-boundary refactorings, and helped draft the low-latency streaming thread design before implementation.

4. **Documentation Review Support:** Helped draft the list of transition blockers (low FPS, broken liveness, poor UI) for the Sprint 6 documentation review. LLMs also produced the updated section in `docs/development-process.md` describing the Raspberry Pi-specific environment variables.

5. **Code Review and Error Diagnosis:** Used for spot-checking error-handling paths in the GPIO/servo abstraction and for suggesting defensive coding patterns around the camera stream initialisation.

Overall LLM usage was lower than in Sprint 3 (Assignment 5). The team relied more on hardware profiling tools and direct debugging once the Pi was available, so LLMs were used primarily for log interpretation and targeted bug fixes rather than for large-scale artifact generation.

No LLM-generated content was merged into `main` without review. Every LLM-assisted patch was read, tested on the target hardware, and approved by a team member before the linked PR was merged, and every code change still had to pass the Assignment 4 CI gates before it was eligible for release.
