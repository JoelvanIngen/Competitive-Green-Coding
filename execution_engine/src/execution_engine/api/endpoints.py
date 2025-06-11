from fastapi import APIRouter

from execution_engine import executor
from execution_engine.models.schemas import ExecuteRequest

router = APIRouter()


@router.post("/execute")
async def execute(request: ExecuteRequest):
    """
    Requests the executor to schedule execution
    """
    await executor.entry(request)


@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "message": "DB service is running"}
