from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from loguru import logger

from db.api import endpoints
from db.config import HOST, PORT


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager
    Anything before `yield` runs on startup, anything after on exit
    """

    logger.info(f"Server started on {HOST}:{PORT}")
    endpoints.create_db_and_tables()

    yield

    logger.info("Server stopped")


app = FastAPI(
    lifespan=lifespan,
)

app.include_router(endpoints.router, prefix="/api")


def main():
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
