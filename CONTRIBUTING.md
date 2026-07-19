# Contributing to FaceGuardV2

This guide describes the current contribution workflow for human contributors working on FaceGuardV2.

## Scope

FaceGuardV2 is maintained as a public course product repository. Contributions must preserve product functionality, traceability, CI evidence, documentation quality, and public/private evidence separation.

## Branch and issue workflow

1. Create or select a GitHub issue before starting work.
2. Use the issue as the source of scope, acceptance criteria, implementer, reviewer, Story Points, and Work Status.
3. Create a separate branch for the issue.
4. Use the branch naming format:

```text
<issue-number>-short-description
```

Example:

```text
82-update-root-readme-for-handover
```

5. Keep each pull request focused on one logical change where practical.
6. Link the pull request to the issue.
7. Do not push directly to `main`.
8. Do not approve your own pull request.
9. Merge only after review and required checks are complete.

## Pull request requirements

Every pull request should include:

* related issue;
* summary of changes;
* testing performed;
* acceptance criteria verification;
* reviewer checklist;
* changelog checklist.

Use the repository pull request template and keep the evidence inspectable.

## Definition of Done

A Product Backlog Item may be marked Done only when the issue-specific acceptance criteria and the maintained Definition of Done are satisfied.

See:

* [docs/definition-of-done.md](docs/definition-of-done.md)
* [docs/testing.md](docs/testing.md)
* [docs/quality-requirements.md](docs/quality-requirements.md)
* [docs/quality-requirement-tests.md](docs/quality-requirement-tests.md)

## Local setup

The current maintained product is in `MVP_v1/`.

Recommended local Docker Compose setup:

```bash
cd MVP_v1
cp .env.example .env
# edit SECRET_KEY, ADMIN_PASSWORD, and other required values
docker compose up --build
```

Open:

```text
http://localhost:8000/login
```

For detailed setup, Raspberry Pi deployment, configuration, user flows, API routes, and known limitations, see:

* [MVP_v1/README.md](MVP_v1/README.md)

## Testing and verification

Run relevant checks before requesting review.

From `MVP_v1/`:

```bash
pytest
```

Recommended targeted checks:

```bash
pytest -m "not qrt"
pytest -m qrt
ruff check app/ tests/
ruff format --check app/ tests/
mypy app/ --ignore-missing-imports
```

If the change affects Docker setup, also verify the Docker build or Docker Compose startup:

```bash
docker compose up --build
```

Document the exact commands you ran in the pull request.

## Documentation updates

Update maintained documentation when a change affects product behavior, setup, architecture, testing, quality gates, access, deployment, or handover.

Common documentation files:

| Change type                                              | Update                                                       |
| -------------------------------------------------------- | ------------------------------------------------------------ |
| Setup, run, deployment, user flows                       | `README.md`, `MVP_v1/README.md`, `docs/customer-handover.md` |
| Customer handover, access, limitations, transition state | `docs/customer-handover.md`                                  |
| Architecture or major service boundary change            | `docs/architecture/README.md` and relevant ADRs              |
| Testing or CI change                                     | `docs/testing.md`, `docs/quality-requirement-tests.md`       |
| Quality requirement change                               | `docs/quality-requirements.md`                               |
| User-facing scenario change                              | `docs/user-acceptance-tests.md`                              |
| Product scope or course outcome change                   | `docs/roadmap.md`, `docs/user-stories.md`                    |
| User-visible change                                      | `CHANGELOG.md`                                               |

## Changelog rules

User-visible changes must be added to `CHANGELOG.md` under `[Unreleased]` using the appropriate category:

* `Added`
* `Changed`
* `Deprecated`
* `Removed`
* `Fixed`
* `Security`

If a change is not user-visible, mark the pull request changelog checklist as not applicable and explain why.

## Security and privacy rules

Never commit:

* real credentials;
* private `.env` files;
* private access instructions;
* private recordings or recording links;
* exact private timecodes;
* unnecessary personal information;
* customer-identifying information;
* production face data or non-sanitized screenshots.

Use `.env.example` for public configuration examples. Keep actual credentials and private customer access details in the private submission channel only.

## Review expectations

The reviewer should check that:

* the pull request is linked to the correct issue;
* acceptance criteria are verified;
* tests and relevant CI checks pass;
* no secrets or private information are committed;
* documentation is updated where needed;
* `CHANGELOG.md` is updated when the change is user-visible;
* the change does not break existing functionality.

## Customer-facing quality

For Assignment 6 and later handover work, treat the public repository entry point and customer-facing documentation as product deliverables. Keep these files current when access, setup, deployment, limitations, troubleshooting, handover status, or support expectations change:

* `README.md`
* `MVP_v1/README.md`
* `docs/customer-handover.md`
* `CONTRIBUTING.md`
* `AGENTS.md`
* `reports/week6/README.md`
* `reports/week7/README.md`
