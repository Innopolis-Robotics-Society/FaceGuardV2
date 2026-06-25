"""FastAPI application entry point.

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Run in Docker (production):
    uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .auth import bootstrap_admin_from_env
from .config import Settings, get_settings
from .database import FaceDatabase
from .ml_client import MLClient
from .recognition import RecognitionLoop
from .routes import auth as auth_routes
from .routes import logs as logs_routes
from .routes import pages as pages_routes
from .routes import status as status_routes
from .routes import stream as stream_routes
from .routes import users as users_routes
from .servo import make_servo
from .state import state

log = logging.getLogger("faceguard")


# ---------------------------------------------------------------------------
# Lifespan: build singletons (DB, ML client, servo, recognition loop),
#           start the background poller, and tear everything down on exit.
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # --- DB ---
    db = FaceDatabase(db_path=settings.database_path)
    bootstrap_admin_from_env(db, settings)
    log.info("DB ready at %s", settings.database_path)

    # --- ML client ---
    ml = MLClient(base_url=settings.ml_service_url)
    await ml.start()

    # --- Servo ---
    servo = make_servo(settings)
    log.info("Servo mode: %s", servo.mode)

    # --- Recognition loop ---
    loop = RecognitionLoop(
        db=db,
        ml=ml,
        servo=servo,
        state=state,
        threshold=settings.threshold,
        interval_ms=settings.recognition_interval_ms,
    )
    await loop.start()

    # Stash on app.state for Depends() to pick up.
    app.state.db = db
    app.state.ml = ml
    app.state.servo = servo
    app.state.loop = loop
    app.state.settings = settings

    try:
        yield
    finally:
        log.info("Shutting down...")
        await loop.stop()
        await ml.close()
        db.close()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


app = FastAPI(
    title="FaceGuard Backend",
    version="0.1.0",
    description="Web admin + recognition orchestration for FaceGuardV2.",
    lifespan=lifespan,
)


# Session middleware (signed cookies).
settings = get_settings()
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key.get_secret_value(),
    session_cookie=settings.session_cookie_name,
    max_age=12 * 3600,  # 12h
    https_only=settings.session_cookie_secure,
    same_site="lax",
)


# Static files (CSS, JS, favicon).
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Register routers.
app.include_router(auth_routes.router)
app.include_router(pages_routes.router)
app.include_router(stream_routes.router)
app.include_router(status_routes.router)
app.include_router(users_routes.router)
app.include_router(logs_routes.router)


# ---------------------------------------------------------------------------
# Dependencies — provide singletons to route handlers.
# ---------------------------------------------------------------------------


def get_db(request) -> FaceDatabase:
    return request.app.state.db


def get_ml(request) -> MLClient:
    return request.app.state.ml


def get_servo(request):
    return request.app.state.servo


# Override module-level Depends used in route signatures.
# (FastAPI lets route handlers declare `db: FaceDatabase = Depends()` and
# we wire that to the request-scoped singleton here.)
from fastapi import Request  # noqa: E402


def _db_dep(request: Request) -> FaceDatabase:
    return request.app.state.db


def _ml_dep(request: Request) -> MLClient:
    return request.app.state.ml


def _settings_dep() -> Settings:
    return get_settings()


# Make the dependency injectors visible to `Depends(...)` lookups.
# The routes use `Depends()` with type hints that match these functions'
# return types, so FastAPI's DI container will pick them up automatically
# if they are declared with matching types — we expose them under the
# expected names for clarity and to keep mypy happy.
app.dependency_overrides[FaceDatabase] = _db_dep
app.dependency_overrides[MLClient] = _ml_dep


@app.get("/healthz")
async def root_healthz():
    return {"status": "ok", "service": "faceguard-backend"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=False,
    )
