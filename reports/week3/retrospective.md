# Sprint Retrospective

## What went well: three specific points

1. **Database layer is solid.** The SQLite schema and `FaceDatabase` abstraction are clean, well-structured, and handle users, guests, and audit logs without issues.
2. **Backend architecture is reliable.** FastAPI lifespan, dependency injection, and route structure are well-organized; the recognition loop and servo abstraction integrate smoothly.
3. **ML service is functional.** InsightFace integration, MJPEG streaming, and the `/ml/latest` endpoint are working correctly and provide stable embeddings for the recognition pipeline.

## What did not go well: three specific points

1. **Raspberry Pi deployment is difficult.** Hardware access (camera, GPIO) and environment setup on the Pi are cumbersome and error-prone, slowing down integration testing.
2. **Frontend behavior is inconsistent.** The UI does not always reflect the current system state correctly (e.g., status updates, stream rendering), leading to a confusing user experience.
3. **Docker build times are too long.** The Dockerfile pulls and compiles heavy dependencies (OpenCV, InsightFace model), making the build process slow and frustrating during development.

## Action points: one or two concrete improvement actions for the next Sprint

1. **Optimize the Dockerfile.** Introduce multi-stage builds, cache model downloads, and use pre-built wheels where possible to drastically reduce build time.
2. **Fix and polish the frontend.** Audit HTMX partials, SSE event handling, and dashboard state synchronization to ensure the UI accurately reflects backend state at all times.
