# Week 3 Reflection

## Learning points

This week, the team learned how to move user stories from a document into GitHub Issues and use them as a real Product Backlog. We understood that stable user story IDs like `US-001` should stay the same, while GitHub issue numbers are used only for tracking work.

During backlog refinement, we learned that some stories were too big and needed to be split into smaller PBIs. 

Estimation helped us compare the size and risk of different tasks. We learned that tasks with unclear requirements or technical risks need more discussion before they can be marked as ready.

Sprint Planning helped us select only the work that was realistic for MVP v1. We also learned to separate Sprint scope from MVP version tracking.

During MVP v1 delivery, we learned that the project needs not only code, but also clear documentation, run instructions, testing evidence, changelog updates, and reviewed PRs.

## Validated assumptions

We confirmed that GitHub Issues are useful for managing the Product Backlog and tracking the current state of user stories.

We confirmed that MVP v1 can be delivered with a web admin interface, backend services, database support, and emulated hardware behavior.

We confirmed that using Docker Compose makes the project easier to run and test on different machines.

We also confirmed that not every Must Have story should automatically be included in MVP v1. The team selected only the stories and supporting tasks that could be completed and reviewed during the Sprint.

Customer review showed that the main MVP v1 flow is understandable, but the next versions should focus more on real recognition quality, hardware integration, and reliable access decisions.

## Friction and gaps

The main difficulty was keeping all project artifacts synchronized: GitHub Issues, `docs/user-stories.md`, milestones, project boards, releases, and Week 3 reports.

Another difficulty was splitting large stories into smaller tasks while keeping links between user stories and supporting PBIs.

There are still technical risks around the real face recognition pipeline. MVP v1 supports development and demonstration, but the real camera, threshold tuning, and hardware behavior still need more testing.

The team also needs stronger verification on the target environment, especially Raspberry Pi and servo control.

The workflow requirements were also challenging because every team member needed to create a PR, review another PR, leave a meaningful comment, and provide evidence.

## Planned response

In the next Sprint, the team will continue using issue-linked branches and reviewed PRs for all changes.

The team will keep `docs/user-stories.md` synchronized with GitHub Issues and use it only as a traceability index.

The next Sprint should focus on reducing the gap between MVP v1 emulation and real hardware behavior. The main priorities are real face recognition, confidence threshold testing, servo control, and safe lock behavior when the user is unknown.

The team will also improve documentation and release preparation by updating `CHANGELOG.md`, run instructions, verification evidence, and release notes as part of the Definition of Done.

Relevant links:

* Current user-story registry: [`docs/user-stories.md`](../../docs/user-stories.md)
* Roadmap: [`docs/roadmap.md`](../../docs/roadmap.md)
* Definition of Done: [`docs/definition-of-done.md`](../../docs/definition-of-done.md)
* Changelog: [`CHANGELOG.md`](../../CHANGELOG.md)
* MVP v1 run instructions: [`README.md`](../../README.md)
* MVP v1 implementation folder: [`MVP_v1/`](../../MVP_v1/)
