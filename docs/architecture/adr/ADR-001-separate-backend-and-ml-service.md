# ADR-001: Separate backend and ML service

**Status:** Accepted  
**Date:** 2026-07-02  
**Quality requirements addressed:** QR-001

## Context

FaceGuardV2 needs camera access, face detection, embedding extraction, recognition decisions, persistence, web UI, authentication, and door-control behavior. Combining all of this in one process would make the backend depend directly on camera and ML libraries and would make local development harder.

## Decision

Keep the backend and ML responsibilities separated.

The ML service owns camera access, frame processing, face detection, and embedding extraction. The FastAPI backend owns admin UI, authentication, comparison against stored embeddings, access decisions, audit logging, status publishing, and servo control.

The backend communicates with the ML service through HTTP endpoints such as `/ml/latest` and `/ml/stream`.

## Consequences and tradeoffs

Positive consequences:

- ML internals can change without rewriting backend routes and persistence.
- Backend recognition decisions can be tested using synthetic embeddings and mocked ML responses.
- The camera boundary is explicit in deployment diagrams and runtime configuration.
- The backend remains responsible for product access decisions.

Tradeoffs:

- Runtime depends on the ML service being healthy and reachable.
- Network/HTTP failure handling is required even in local deployments.
- The registration and recognition workflows must account for missing or stale ML data.

## Related architecture views

| View | Rendered diagram | Source artifact |
|---|---|---|
| Static view | [component-diagram.png](../static-view/component-diagram.png) | [component-diagram.puml](../static-view/component-diagram.puml) |
| Dynamic view | [register-new-person-sequence.png](../dynamic-view/register-new-person-sequence.png) | [register-new-person-sequence.puml](../dynamic-view/register-new-person-sequence.puml) |
| Deployment view | [deployment-diagram.png](../deployment-view/deployment-diagram.png) | [deployment-diagram.puml](../deployment-view/deployment-diagram.puml) |

This ADR is visible in all three views: the static view shows the backend and ML service as separate components, the dynamic view shows backend-to-ML calls during registration, and the deployment view shows the services as separate runtime containers.
