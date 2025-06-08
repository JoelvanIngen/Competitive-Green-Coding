from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from loguru import logger

from db.api import endpoints
from db.config import settings
from db.engine import create_db_and_tables


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager
    Anything before `yield` runs on startup, anything after on exit
    """

    logger.info(f"Server started on {settings.DB_HANDLER_HOST}:{settings.DB_HANDLER_PORT}")
    create_db_and_tables()
    logger.info("Database and tables created")

    yield

    logger.info("Server stopped")


app = FastAPI(
    lifespan=lifespan,
)

app.include_router(endpoints.router, prefix="/api")


def main():
    uvicorn.run(app, host=settings.DB_HANDLER_HOST, port=settings.DB_HANDLER_PORT)


if __name__ == "__main__":
    main()
