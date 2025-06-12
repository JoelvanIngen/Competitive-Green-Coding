import asyncio

from fastapi import APIRouter

from execution_engine import executor
from execution_engine.models.schemas import ExecuteRequest

router = APIRouter()


@router.post("/execute")
async def execute(request: ExecuteRequest):
    """
    Requests the executor to schedule execution
    """
    # Create task so we can immediate return success so frontend can show "Submission posted"
    await asyncio.create_task(executor.entry(request))
    return {"status": "success"}


@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "message": "Engine service is running"}
