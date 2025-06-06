from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from loguru import logger

from execution_engine.api import endpoints
from execution_engine.config import HOST, PORT


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager
    Anything before `yield` runs on startup, anything after on exit
    """

    logger.info(f"Server started on {HOST}:{PORT}")
    # TODO: Pulling docker images?

    yield

    logger.info("Server stopped")
    # TODO: Gracefully shut down any lingering Docker services


app = FastAPI(
    lifespan=lifespan,
)

# Prevents us having to put "/api" in every routing decorator (allegedly)
app.include_router(endpoints.router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
