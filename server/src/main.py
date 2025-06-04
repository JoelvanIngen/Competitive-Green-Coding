from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from loguru import logger

from api import router
from .config import HOST, PORT


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager
    Anything before `yield` runs on startup, anything after on exit
    """

    logger.info(f"Server started on {HOST}:{PORT}")
    # TODO: Pulling docker images?

    yield

    logger.info(f"Server stopped")
    # TODO: Gracefully shut down any lingering Docker services


app = FastAPI(
    lifespan=lifespan,
)

# Prevents us having to put "/api" in every routing decorator
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
