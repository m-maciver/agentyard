"""
AgentYard — FastAPI application entry point
Run: uvicorn main:app --reload
"""
import logging
import sys
import os

# Ensure backend/ is on sys.path so `from config import ...` works
sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import init_db
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

# CORS — allow all origins for MVP (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(jobs.router)
app.include_router(admin.router)
app.include_router(webhooks.router)


@app.get("/health", tags=["system"])
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0", "env": settings.app_env}


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
