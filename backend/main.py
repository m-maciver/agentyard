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

from api.database import init_db, engine
from api.routers import agents, auth, jobs, admin, webhooks
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

# CORS — restricted to known frontend origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://getramble.xyz",
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
