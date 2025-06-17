import asyncio

from fastapi import APIRouter

from common.schemas import SubmissionCreate
from execution_engine import executor

router = APIRouter()


@router.post("/execute")
async def execute(request: SubmissionCreate):
    """
    Requests the executor to schedule execution
    """
    # Create task so we can immediate return success so frontend can show "Submission posted"
    await asyncio.create_task(executor.entry(request))
    return {"status": "success"}


@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "message": "Engine service is running"}
