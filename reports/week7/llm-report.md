# LLM Usage in FaceGuard Project — Assignment 7

During Sprint 5 (Assignment 7 / Week 7), Large Language Models (LLMs) were utilized for the following tasks:

1. **Frontend Design and CSS Refactoring:** Assisted in restructuring `custom.css` and the Jinja2 templates (`dashboard.html`, `users.html`, `user_detail.html`, `register.html`, `login.html`, `logs.html`) for visual consistency, adaptive layout, and mobile responsiveness. LLMs suggested color-scheme harmonization, table-styling patterns, and partial-template decomposition that replaced the high-contrast dark tables flagged by the customer in Week 6.

2. **Backend Cleanup and Optimization:** Reviewed the refactored `database.py`, `recognition.py`, and `routes/users.py` for redundant embedding copies and expensive packet structures. LLMs proposed cleaner route boundaries, validation patterns, and SQL index hints that were merged in PR #124.

3. **ML Service Optimization and Liveness Fixes:** Supported the switch from the active eye-blink challenge to a passive, faster liveness model in `ml_service/main.py`. LLMs helped debug the blink-counter logic, adjust the frame-sampling window for the Raspberry Pi camera stream, and restructure background inference into a dedicated thread. The Dockerfile and `requirements.txt` were also reviewed for unnecessary dependencies.

4. **Documentation Expansion:** Drafted the expanded root README sections for deployment steps, operating conditions, and launch guides (PR #122). LLMs also helped update the UAT execution results in `docs/user-acceptance-tests.md` to reflect the post-optimization verification runs.

5. **Transition Readiness Review:** Reviewed `docs/customer-handover.md` against the Week 6 customer requests. LLMs suggested recovery-instruction wording, environment-variable clarity, and troubleshooting-table entries that were incorporated into the handover document.

Overall LLM usage in Week 7 was lower than in Sprint 3 (Assignment 5) and focused on targeted refactoring, design polish, and documentation updates rather than large-scale artifact generation. The team relied more on direct template editing, hardware profiling, and peer review once the PR scope was defined.

No LLM-generated content was merged into `main` without review. Every LLM-assisted patch was read, tested on the target hardware or in CI, and approved by a team member before the linked PR was merged, and every code change still had to pass the full CI gate (ruff, ruff format, mypy, Docker build, unit tests, integration tests, QRTs, coverage, `pip-audit`, Lychee) before it was eligible for the final delivery.
