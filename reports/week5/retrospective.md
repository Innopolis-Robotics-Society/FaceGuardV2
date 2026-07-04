# Sprint Retrospective — Sprint 3 (Week 5)

## What went well

- Liveness detection was successfully implemented and integrated into
  the recognition pipeline.
- Backend data layer was refactored — all database interactions now go
  through a single typed interface, making the codebase cleaner and
  easier to maintain.
- Audit log output was improved: logs are now accessible and filterable
  through the web interface.

## What did not go well

- Backend refactoring consumed more time than estimated, which left less
  capacity for other planned features.
- Test coverage expansion took longer than expected due to async testing
  infrastructure issues.

## What the team changed or attempted to change based on the previous Sprint Retrospective, and what results they observed

- **Mandatory Interface Analysis (4.1):** Applied during the data layer
  redesign — all database operations were mapped before implementation
  began. Result: the refactor landed without breaking existing routes.
- **Upstream Product Research (4.2):** Applied to liveness detection —
  existing approaches were benchmarked against hardware constraints
  before implementation. Result: a working solution was delivered within
  the sprint.

## Action points

1. **Improve sprint capacity estimation.** Refactoring and
   infrastructure tasks consistently exceed initial estimates — apply
   a 1.5× buffer during planning to prevent feature work from being
   crowded out.
2. **Define integration checkpoints for new pipeline components.** Any
   new module touching the recognition pipeline should have a
   mid-sprint integration check to catch compatibility issues early.
