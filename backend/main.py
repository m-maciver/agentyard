"""
AgentYard — FastAPI application entry point
Run: uvicorn main:app --reload
"""
import logging
import sys
import os
import time

# Ensure backend/ is on sys.path so `from config import ...` works
sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.database import init_db, engine
from api.routers import agents, auth, jobs, admin, webhooks, wallets
from config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info(f"AgentYard starting — env={settings.app_env}, db={settings.database_url[:40]}...")

    # Auto-create tables for SQLite local dev
    if settings.is_sqlite:
        await init_db()
        logger.info("SQLite tables created")

    yield

    logger.info("AgentYard shutting down")


app = FastAPI(
    title="AgentYard",
    description="Lightning-native marketplace where AI agents hire AI agents",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — restricted to known frontend origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://frontend-xi-three-92.vercel.app",
    "https://agentyard.xyz",
    "https://getramble.xyz",
    # Note: in production, remove the wildcard below and keep only specific origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log every request: method, path, status, duration."""
    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 1)
    logger.info(
        "%s %s → %d (%sms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# Routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(jobs.router)
app.include_router(admin.router)
app.include_router(webhooks.router)
app.include_router(wallets.router)


@app.get("/health", tags=["system"])
async def health():
    """Health check — returns db connectivity status. Returns 503 if DB is unreachable."""
    from sqlalchemy import text
    from sqlalchemy.exc import SQLAlchemyError
    from fastapi.responses import JSONResponse

    db_status = "error"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except SQLAlchemyError as e:
        logger.error("Health check DB ping failed: %s", e)

    payload = {"status": "ok", "version": "0.1.0", "db": db_status}
    status_code = 200 if db_status == "connected" else 503
    return JSONResponse(content=payload, status_code=status_code)


@app.get("/health/diagnose", tags=["system"])
async def health_diagnose():
    """
    Detailed diagnostic check — returns system status including DB, Lightning, agent stats,
    and active jobs. Useful for debugging and the `agentyard doctor` command.
    """
    from sqlalchemy import text, func
    from sqlalchemy.exc import SQLAlchemyError
    from fastapi.responses import JSONResponse
    from datetime import datetime, timezone, timedelta
    from api.database import get_session
    from api.models import AgentProfile, Job, JobStatus

    checks = {}
    warnings = []
    now = datetime.now(timezone.utc)
    timestamp = now.isoformat()

    # ── Database ──────────────────────────────────────────────────────────────
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except SQLAlchemyError as e:
        logger.error("Diagnose: DB ping failed: %s", e)
        checks["database"] = "error"
        warnings.append("Database unreachable — API will fail for most requests")

    # ── Lightning ─────────────────────────────────────────────────────────────
    lightning_stub = os.environ.get("LIGHTNING_STUB", "").lower() in ("true", "1") or \
        settings.lnbits_url in ("stub", "", "https://demo.lnbits.com")
    if lightning_stub:
        checks["lightning"] = "stub_mode"
        warnings.append("Lightning in stub mode — real payments disabled")
    else:
        checks["lightning"] = "live"

    # ── Agent + Job stats (if DB is up) ──────────────────────────────────────
    if checks["database"] == "connected":
        try:
            from sqlalchemy.ext.asyncio import AsyncSession
            async with AsyncSession(engine) as session:
                # Total registered agents
                result = await session.execute(
                    text("SELECT COUNT(*) FROM agentprofile WHERE is_active = 1 OR is_active = TRUE")
                )
                checks["agents_registered"] = result.scalar_one_or_none() or 0

                # Protection pool
                from api.utils.platform_stats import get_pool_balance
                try:
                    checks["protection_pool_sats"] = get_pool_balance()
                except Exception:
                    checks["protection_pool_sats"] = 0

                # Active jobs (in_progress + escrowed + delivered)
                active_statuses = ("in_progress", "escrowed", "delivered", "disputed")
                status_placeholders = ", ".join(f"'{s}'" for s in active_statuses)
                result = await session.execute(
                    text(f"SELECT COUNT(*) FROM job WHERE status IN ({status_placeholders})")
                )
                checks["jobs_active"] = result.scalar_one_or_none() or 0

                # Jobs completed in last 24h
                cutoff = (now - timedelta(hours=24)).isoformat()
                result = await session.execute(
                    text(f"SELECT COUNT(*) FROM job WHERE status = 'completed' AND completed_at >= '{cutoff}'")
                )
                checks["jobs_completed_24h"] = result.scalar_one_or_none() or 0

        except Exception as e:
            logger.warning("Diagnose: stats query failed: %s", e)
            checks["agents_registered"] = "unavailable"
            checks["jobs_active"] = "unavailable"
            checks["jobs_completed_24h"] = "unavailable"
    else:
        checks["agents_registered"] = "unavailable"
        checks["protection_pool_sats"] = "unavailable"
        checks["jobs_active"] = "unavailable"
        checks["jobs_completed_24h"] = "unavailable"

    overall_status = "ok" if not any(v == "error" for v in checks.values()) else "degraded"

    payload = {
        "status": overall_status,
        "timestamp": timestamp,
        "version": "0.1.0",
        "checks": checks,
        "warnings": warnings,
    }
    http_status = 200 if overall_status == "ok" else 503
    return JSONResponse(content=payload, status_code=http_status)


@app.get("/", tags=["system"])
async def root():
    """Root redirect to docs."""
    return {
        "name": "AgentYard API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
