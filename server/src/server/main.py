from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from loguru import logger

from server.api import endpoints, endpoints_dev
from server.config import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager
    Anything before `yield` runs on startup, anything after on exit
    """

    logger.info(f"Server started on {settings.SERVER_HOST}:{settings.SERVER_PORT}")

    yield

    logger.info("Server stopped")


app = FastAPI(
    lifespan=lifespan,
)

# Prevents us having to put "/api" in every routing decorator
app.include_router(endpoints.router, prefix="/api")
app.include_router(endpoints_dev.router, prefix="/dev")

if __name__ == "__main__":
    uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT)
