import logging

from fastapi import FastAPI

from app.api import api_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.name)
app.include_router(api_router)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("api_startup", extra={"environment": settings.env})
