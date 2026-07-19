
# Customer Handover Guide

This document describes the current handover state of FaceGuardV2 — what has been delivered, what the customer can already do with it, and what is still pending before final acceptance. For how to actually set up, deploy, and use the product, see the linked documentation below rather than duplicating those steps here.

## 1. Product overview

FaceGuardV2 is a face-recognition access-control system for a laboratory door. See [architecture.md](architecture.md) for how it's built and [getting-started.md](getting-started.md) / [deployment-raspberry-pi.md](deployment-raspberry-pi.md) for how to run it.

The current maintained product is located in `MVP_v1/`. The historical prototype in `MVP_v0/` is kept for traceability only and should not be treated as the current handover version.

## 2. Current handover status

### Handover level

```text
Independently used by customer
```

This means that, beyond having a runnable product version and customer-facing documentation available, the customer directly interacted with the running trial during the Week 7 session — exercising the live dashboard, the LED status indicators, and the audit log — rather than only observing a team-led walkthrough.

### Customer confirmation status

```text
Accepted
```

During the Week 7 transition-confirmation session, the customer confirmed satisfaction with the current state of the project and explicitly accepted this document as sufficient for the reached handover level. See [§10](#10-status-update-procedure) for when this status must be revisited.

### Current transition state

| Area | Current state |
| --- | --- |
| Repository access | Available through the FaceGuardV2 GitHub repository. |
| Product access | Latest GitHub release, or running `MVP_v1/` locally/on Raspberry Pi with Docker Compose — see [getting-started.md](getting-started.md) and [deployment-raspberry-pi.md](deployment-raspberry-pi.md). |
| Customer-side operation | Not yet confirmed on customer-owned infrastructure. The Week 7 trial ran on the team's Raspberry Pi deployment. |
| Customer independent use | Confirmed. During the Week 7 trial, the customer directly interacted with the live dashboard, LED indicators, and audit log. |
| Ownership transfer | Completed. The repository has been transferred to the customer. |
| Private credentials | Not stored in the public repository. Share only through a private, customer-approved channel. |
| Final transition | Confirmed. The customer accepted the Week 7 transition (see above). |

## 3. Repository and ownership arrangements

The repository is public and contains sanitized product code, documentation, reports, and public evidence. It must not contain private credentials, private access instructions, private recordings, exact private timecodes, customer-identifying information, or real biometric datasets.

**Available for customer/reviewer inspection:** public source code, current maintained implementation (`MVP_v1/`), setup/run documentation, release artifacts, changelog and release history, test and quality documentation.

**Intentionally not committed to the public repository:** real credentials, `.env` files with real values, private deployment credentials, private customer communication/recordings/timecodes, private acceptance evidence, real production face images or biometric data. These are shared only through a private, customer-approved channel.

## 4. Using the product

- First run / local demo: [getting-started.md](getting-started.md)
- Raspberry Pi deployment: [deployment-raspberry-pi.md](deployment-raspberry-pi.md)
- Day-to-day usage of the admin UI: [user-guide.md](user-guide.md)
- All configuration options: [configuration.md](configuration.md)
- Data backup / recovery: [deployment-raspberry-pi.md, §9](deployment-raspberry-pi.md#9-data-persistence) (where the database lives and what to back up before any destructive operation)
- If something isn't working: [troubleshooting.md](troubleshooting.md)

The ML service is internal and not intended to be used directly by the customer — the admin web UI is the customer-facing interface.

## 5. Verification checklist

Before treating a deployment as accepted, work through the checklist in [deployment-raspberry-pi.md, §8](deployment-raspberry-pi.md#8-verify-the-deployment) (or the equivalent local steps in [getting-started.md, §4](getting-started.md#4-try-the-golden-path)): containers running, health check, login, registration, recognition (granted and denied), and — on Raspberry Pi — physical servo actuation.

## 6. Secrets policy

The customer must keep private: the admin password, session `SECRET_KEY`, private deployment credentials, private network addresses (if not intended for public sharing), and any real face/biometric data. Only sanitized examples belong in the public repository. See [configuration.md](configuration.md) for what each secret-bearing variable controls.

## 7. Known limitations

- This is a course MVP, not a certified physical security system.
- Real deployment requires controlled lighting, stable camera placement, and hardware testing; recognition quality depends on camera quality, registration sample quality, threshold tuning, and ML service behavior.
- HTTPS termination is not provided by the application itself — handle it at the deployment/infrastructure layer if needed.
- Multi-admin operational management is limited (single bootstrapped admin account).
- Liveness (blink-check) sensitivity is currently hardcoded in the ML service rather than fully controlled by the documented `.env` liveness variables — see [troubleshooting.md](troubleshooting.md) ("Liveness / blink check seems to block valid users") if it seems too strict or too loose.
- Long-term deployment and operation on customer-owned infrastructure (e.g. the physical lab door) has not yet been confirmed; the Week 7 trial ran on the team's Raspberry Pi deployment.
- Final customer acceptance was confirmed during Week 7 (see [§2](#2-current-handover-status)).

See [architecture.md, "Known limitations"](architecture.md#known-limitations) for the technical/architectural limitations behind these.

## 8. Documentation entry points

| Need | Document |
| --- | --- |
| Public project overview | [../README.md](../README.md) |
| Quick local demo | [getting-started.md](getting-started.md) |
| Raspberry Pi deployment | [deployment-raspberry-pi.md](deployment-raspberry-pi.md) |
| Architecture | [architecture.md](architecture.md) |
| Configuration reference | [configuration.md](configuration.md) |
| Admin UI user guide | [user-guide.md](user-guide.md) |
| Troubleshooting | [troubleshooting.md](troubleshooting.md) |
| Backend developer reference | [../MVP_v1/README.md](../MVP_v1/README.md) |
| Changelog | [../CHANGELOG.md](../CHANGELOG.md) |
| Contributor guide | [../CONTRIBUTING.md](../CONTRIBUTING.md) |

Course/internal artifacts (backlog, roadmap, process, QA evidence) are indexed separately in the root [README.md](../README.md) and are not required reading to use the product.

## 9. Remaining support needs

The current documentation set is sufficient for the reached handover level (`Independently used by customer`). Before a stronger handover level (`Deployed or operated on customer side`) can be claimed, the following is still needed:

- customer-side Raspberry Pi deployment on the actual lab door, if the customer proceeds with hardware-side operation beyond the course.

## 10. Status update procedure

This document must be updated whenever any of the following changes: product access artifact, release version, deployment method, environment variables, secrets-handling expectations, customer feedback, customer acceptance status, handover level, limitations, or support expectations.

At minimum, update these fields on any customer-facing status change:

```text
Handover level
Customer confirmation status
Current transition state
Known limitations
Remaining support needs
```

## 11. Public/private evidence separation

Public repository documents may include sanitized summaries only. Do not publish private recordings, exact private timecodes, private credentials or access links, customer-identifying screenshots, private acceptance-confirmation screenshots, or real biometric data. Private confirmation evidence, credentials, and customer messages must be placed in an instructor/customer-approved private channel, not this repository.
