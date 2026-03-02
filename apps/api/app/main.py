import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import close_redis, init_redis
from app.services.model_store import model_store

settings = get_settings()
configure_logging(settings.app_log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    await init_redis()
    try:
        model_store.load(settings.artifact_path)
        logger.info("model_store_loaded", extra={"artifact_path": settings.artifact_path})
    except Exception as exc:  # noqa: BLE001
        logger.warning("model_store_not_loaded", extra={"error": str(exc), "artifact_path": settings.artifact_path})
    logger.info("api_startup", extra={"environment": settings.app_env})
    yield
    await close_redis()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
