from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from config import HOST, PORT


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager
    Anything before `yield` runs on startup, anything after on exit
    """

    # TODO: Logging
    # TODO: Pulling docker images

    yield

    # TODO: Logging
    # TODO: Gracefully shut down any lingering Docker services


app = FastAPI(
    lifespan=lifespan,
)


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
