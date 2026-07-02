# ADR-004: Use servo abstraction with emulated mode

**Status:** Accepted  
**Date:** 2026-07-02  
**Quality requirements addressed:** QR-004

## Context

FaceGuardV2 controls a physical servo and LED in Raspberry Pi deployment, but the team also needs to develop, test, and demonstrate the product on laptops where GPIO hardware is unavailable.

## Decision

Use a servo-controller abstraction with two runtime modes:

- `gpio` mode for Raspberry Pi hardware deployment;
- `emulated` mode for local development, CI-adjacent checks, and review without hardware.

Runtime mode is supplied through environment configuration.

## Consequences and tradeoffs

Positive consequences:

- The same backend recognition flow can trigger door behavior in both real and emulated environments.
- Servo behavior can be covered by automated tests.
- Reviewers can inspect the product without requiring the physical lock hardware.

Tradeoffs:

- Emulated mode cannot fully prove real wiring, timing, or mechanical behavior.
- Hardware acceptance still requires manual or customer-side validation on Raspberry Pi.
- Environment configuration must be checked carefully before a hardware deployment.

## Related architecture views

| View | Rendered diagram | Source artifact |
|---|---|---|
| Static view | [component-diagram.png](../static-view/component-diagram.png) | [component-diagram.puml](../static-view/component-diagram.puml) |
| Deployment view | [deployment-diagram.png](../deployment-view/deployment-diagram.png) | [deployment-diagram.puml](../deployment-view/deployment-diagram.puml) |

This ADR is visible in the static view through the Servo Controller component and external Servo + LED device. It is visible in the deployment view through the Raspberry Pi hardware boundary and the emulated mode used on development laptops.
