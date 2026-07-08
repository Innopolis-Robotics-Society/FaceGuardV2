# Agent Guidance for FaceGuardV2

This document gives instructions for AI coding agents, automation agents, and LLM-assisted contributors working in the FaceGuardV2 repository.

## Primary rule

Do not make broad or speculative changes. Work only on the issue scope, preserve existing course evidence, and keep public/private artifact separation intact.

## Product context

FaceGuardV2 is a face-recognition access-control system for a laboratory door. The maintained product is in `MVP_v1/` and uses:

* FastAPI backend;
* web admin UI;
* separate ML service boundary;
* SQLite persistence;
* recognition orchestration;
* audit logging;
* servo abstraction for Raspberry Pi GPIO or emulated mode;
* Docker Compose setup;
* pytest-based automated tests;
* GitHub Actions CI.

Historical prototype code is in `MVP_v0/` and should not be treated as the current product unless an issue explicitly asks for it.

## Important repository paths

| Path                                | Meaning                                                 |
| ----------------------------------- | ------------------------------------------------------- |
| `MVP_v1/`                           | Current maintained product implementation.              |
| `MVP_v1/app/`                       | Backend application code.                               |
| `MVP_v1/tests/`                     | Unit, integration, and quality requirement tests.       |
| `MVP_v1/.env.example`               | Public sanitized configuration example.                 |
| `docs/`                             | Maintained documentation.                               |
| `docs/customer-handover.md`         | Customer-facing handover state and transition guidance. |
| `docs/architecture/`                | Architecture views and ADRs.                            |
| `docs/testing.md`                   | Testing and CI status.                                  |
| `docs/quality-requirements.md`      | Maintained quality requirements.                        |
| `docs/quality-requirement-tests.md` | Automated quality requirement tests.                    |
| `docs/user-acceptance-tests.md`     | UAT scenarios and execution status.                     |
| `reports/`                          | Public weekly report evidence.                          |
| `.github/`                          | GitHub workflow, issue, and PR configuration.           |

## Change discipline

When modifying the repository:

1. Keep the change focused on the linked issue.
2. Do not rename or move files unless required.
3. Do not delete assignment evidence, reports, releases, screenshots, transcripts, notes, or historical artifacts.
4. Do not rewrite history.
5. Do not bypass the pull request workflow.
6. Do not disable tests, quality gates, or CI checks unless the issue explicitly requires replacing them with equivalent or stronger checks.
7. If behavior changes, update the relevant maintained documentation in the same PR or in a linked follow-up issue.

## Public/private safety

Never add to the public repository:

* private credentials;
* real `.env` files;
* private customer access instructions;
* raw recordings or private recording links;
* exact private timecodes;
* customer-identifying details;
* unnecessary personal information;
* production face images or real biometric datasets;
* non-sanitized screenshots or videos.

Use sanitized demo data in public examples, screenshots, reports, and videos.

## Configuration rules

Use `.env.example` for public examples. Do not commit `.env`.

When changing configuration behavior, check and update:

* `MVP_v1/.env.example`;
* `MVP_v1/README.md`;
* `README.md` if the public entry point changes;
* `docs/customer-handover.md` if the customer needs to know the new setup, deployment, or secrets-handling step.

## Testing expectations

Prefer running relevant commands from `MVP_v1/`.

Common checks:

```bash
pytest
pytest -m "not qrt"
pytest -m qrt
ruff check app/ tests/
ruff format --check app/ tests/
mypy app/ --ignore-missing-imports
```

For deployment or packaging changes, also verify Docker behavior where practical:

```bash
docker compose up --build
```

Do not claim tests passed unless they were actually run or CI evidence exists.

## Documentation expectations

Update documentation when changing:

* user-facing behavior;
* setup or run commands;
* deployment steps;
* environment variables;
* authentication or secrets handling;
* recognition behavior;
* servo/hardware behavior;
* database schema or persistence behavior;
* API endpoints;
* testing, CI, quality requirements, or UAT;
* handover status or known limitations.

Use relative links for repository-resident documentation where practical.

## Changelog expectations

For user-visible changes, update `CHANGELOG.md` under `[Unreleased]`.

Use categories:

* `Added`
* `Changed`
* `Deprecated`
* `Removed`
* `Fixed`
* `Security`

If a change is internal only, explain in the PR why no changelog entry is needed.

## Handover-specific instructions

For Assignment 6 and final transition work, keep these files aligned:

* `README.md`
* `MVP_v1/README.md`
* `docs/customer-handover.md`
* `CONTRIBUTING.md`
* `AGENTS.md`
* `reports/week6/README.md`
* `reports/week7/README.md`

If product access, setup, deployment, limitations, support expectations, or transition status changes, update the handover-related files before merging.

## Agent output quality

When generating code or documentation:

* be specific to FaceGuardV2;
* avoid generic filler;
* preserve current terminology;
* keep Markdown readable in GitHub;
* do not invent completed customer acceptance, deployment, or transition status;
* mark unknown or pending handover status honestly;
* prefer concise customer-facing explanations over long internal reasoning.
