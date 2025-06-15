import uvicorn

from execution_engine.api import endpoints
from execution_engine.app import app
from execution_engine.config import settings

# Prevents us having to put "/api" in every routing decorator (allegedly)
app.include_router(endpoints.router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(app, host=settings.EXECUTION_ENGINE_HOST, port=settings.EXECUTION_ENGINE_PORT)
