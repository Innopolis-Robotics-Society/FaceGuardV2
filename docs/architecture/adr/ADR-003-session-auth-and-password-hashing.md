# ADR-003: Use session authentication and password hashing

**Status:** Accepted  
**Date:** 2026-07-02  
**Quality requirements addressed:** QR-003

## Context

The web admin interface can register users, manage guests, view logs, and affect access-control behavior. These operations must not be exposed without authentication. The system also must not store or compare plain-text passwords.

## Decision

Use session-based authentication for the admin UI and store password hashes instead of plain-text passwords.

The backend validates the admin session before protected operations such as registration, user/guest management, logs, and dashboard access. The bootstrap admin credentials are supplied through environment configuration, and the stored credential is represented as a password hash.

## Consequences and tradeoffs

Positive consequences:

- Admin-only operations are protected by one backend authentication boundary.
- Password verification can be tested automatically.
- Runtime credentials can be changed through environment configuration without committing secrets.

Tradeoffs:

- Session security depends on correct `SECRET_KEY` management.
- Deployments exposed beyond a trusted local network need HTTPS and secure cookie configuration.
- Password reset and multi-admin management may need further design later.

## Related architecture views

| View | Rendered diagram | Source artifact |
|---|---|---|
| Static view | [component-diagram.png](../static-view/component-diagram.png) | [component-diagram.puml](../static-view/component-diagram.puml) |
| Dynamic view | [register-new-person-sequence.png](../dynamic-view/register-new-person-sequence.png) | [register-new-person-sequence.puml](../dynamic-view/register-new-person-sequence.puml) |

This ADR is visible in the static view through the separated Auth Module. It is visible in the dynamic view because the registration workflow starts with session validation before protected registration logic is executed.
