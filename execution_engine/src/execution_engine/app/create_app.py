from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from execution_engine.config import settings
from execution_engine.executor import scheduler


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    """
    Lifespan context manager
    Anything before `yield` runs on startup, anything after on exit
    """

    logger.info(
        f"Server started on {settings.EXECUTION_ENGINE_HOST}:{settings.EXECUTION_ENGINE_PORT}"
    )
    scheduler.init()

    yield

    logger.info("Server stopped")


app = FastAPI(
    lifespan=_lifespan,
)
