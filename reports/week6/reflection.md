# Week 6 Reflection

## Learning points

Deploying `MVP v2` on Raspberry Pi for the trial release taught us that thresholds and performance assumptions validated on x86 do not transfer one-to-one to ARM hardware. The `buffalo_sc` model runs within acceptable latency on the Pi, but the recognition pipeline required buffer-size tuning and frame-skip adjustments to reach usable FPS.

The documentation review surfaced three concrete gaps before the customer meeting: low video-stream FPS, a non-functional liveness-detection path, and poor web-UI design. Writing these down as tracked blockers rather than informal complaints forced us to assign owners and acceptance criteria to each item.

The Week 6 customer meeting confirmed that the product direction is correct. The customer asked for higher FPS and an improved website design, while explicitly stating that the core recognition and anti-spoofing behaviour is "completely sufficient for the current scope." This gave us permission to spend the remaining Sprint capacity on polish and performance rather than new features.

Fixing the liveness detection on real hardware showed that the active eye-blink challenge works, but only after we adjusted the randomized timer range and the frame-sampling window for the Pi Camera's throughput. The algorithm was correct; the integration constants were not.

## Validated assumptions

We confirmed that `buffalo_sc` is a viable CPU-only model on Raspberry Pi 4. Recognition latency stays within the QRT threshold after the frame-skip optimisation.

We confirmed that the active liveness check (randomised eye-blink challenge) can be made robust on the target device. Static photographs are rejected reliably once the camera FPS and inference batch size are tuned.

We confirmed that the customer prioritises recognition quality, spoofing resistance, and a responsive web UI over additional dashboard pages or administrative features. This validates the decision to keep the Sprint 6 scope focused on optimisation and hardening.

We confirmed that the `.env`-driven configuration and `SERVO_MODE=emulated` fallback remain useful during the transition to hardware deployment. No new configuration gaps were discovered on the Pi.

## Friction and gaps

The primary blocker discovered during the trial release was non-functional liveness detection on Raspberry Pi. The same code that rejected static photos on x86 failed silently on the Pi because the camera stream delivered frames at a lower rate than the challenge timer expected. This was resolved by widening the blink-detection window and lowering the inference frequency, but the debugging cycle consumed a full day.

Low video-stream FPS was the second major friction point. The raw camera feed was usable for debugging but not for a smooth user experience. We traced the bottleneck to unthrottled frame processing in the recognition loop and implemented a dedicated streaming thread with reduced resolution.

The web UI design was flagged as poor during the documentation review. The HTML templates and CSS from `MVP v2` are functional but visually inconsistent and not mobile-friendly. This gap does not block deployment, but it directly affects the customer-facing impression of the product.

Backend optimisation was still in progress at the end of Week 6. Several hot paths in the CRUD layer and the recognition loop had been profiled, but the refactor PRs had not yet been merged. We kept the changes small and reviewable to avoid destabilising the release branch.

## Planned response

In the next Sprint, the team will finish the backend optimisation PRs and merge them after passing the full CI gate (ruff, mypy, unit tests, integration tests, QRTs, coverage, `pip-audit`, Lychee).

The team will raise the video-stream FPS by implementing a separate low-latency streaming thread and by reducing the camera preview resolution. The target is a stable 15–20 FPS on Raspberry Pi 4.

The team will redesign the web UI templates and CSS to improve visual consistency and mobile responsiveness. The customer explicitly requested this, so it will be treated as a Sprint 7 priority rather than a nice-to-have.

The team will keep the liveness-detection parameters tunable via environment variables (`LIVENESS_WINDOW`, `BLINK_THRESHOLD`) and document them in `docs/development-process.md` and the root `README.md`.

The team will prepare the final product delivery once the FPS, UI, and backend optimisation items are closed. The release will be tagged and the CHANGELOG updated in the same PR.

Relevant links:

* Architecture documentation: [`docs/architecture/README.md`](../../docs/architecture/README.md)
* ADR directory: [`docs/architecture/adr/`](../../docs/architecture/adr/)
* Development process and configuration management: [`docs/development-process.md`](../../docs/development-process.md)
* Definition of Done: [`docs/definition-of-done.md`](../../docs/definition-of-done.md)
* Testing status: [`docs/testing.md`](../../docs/testing.md)
* Quality requirements: [`docs/quality-requirements.md`](../../docs/quality-requirements.md)
* Quality requirement tests: [`docs/quality-requirement-tests.md`](../../docs/quality-requirement-tests.md)
* Roadmap: [`docs/roadmap.md`](../../docs/roadmap.md)
* Changelog: [`CHANGELOG.md`](../../CHANGELOG.md)
* MVP v2 run instructions: [`README.md`](../../README.md)
