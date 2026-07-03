# ADR-002: Use SQLite through FaceDatabase DAL

**Status:** Accepted  
**Date:** 2026-07-02  
**Quality requirements addressed:** QR-002, QR-005

## Context

The MVP needs to store permanent users, temporary guests, admin accounts, face embeddings, and recognition audit logs. The product is currently a small single-host access-control prototype, so introducing a separate database server would increase deployment complexity.

## Decision

Use SQLite for MVP persistence and route all SQL access through the `FaceDatabase` data access layer.

The backend stores the SQLite file as a persistent runtime artifact, mounted outside the backend container under `/data`. Product modules should not directly duplicate SQL access; recognition, auth, user management, guest handling, and logging should use the DAL.

## Consequences and tradeoffs

Positive consequences:

- The deployment remains simple and works on Raspberry Pi and local development laptops.
- Tests can exercise critical persistence logic without a separate DB service.
- Guest expiry and audit logging have a central persistence boundary.
- The database file can persist across container rebuilds.

Tradeoffs:

- SQLite is not designed for high-concurrency multi-node deployments.
- Schema changes need careful handling as the product grows.
- Backup and recovery are operational responsibilities for real deployments.

## Related architecture views

| View | Rendered diagram | Source artifact |
|---|---|---|
| Static view | [component-diagram.png](../static-view/component-diagram.png) | [component-diagram.puml](../static-view/component-diagram.puml) |
| Deployment view | [deployment-diagram.png](../deployment-view/deployment-diagram.png) | [deployment-diagram.puml](../deployment-view/deployment-diagram.puml) |

This ADR is visible in the static view through the `FaceDatabase` data access layer and SQLite database. It is visible in the deployment view through the persistent SQLite file mounted outside the backend container.
