import asyncio

from fastapi import APIRouter

from common.schemas import SubmissionCreate
from execution_engine import executor

router = APIRouter()


@router.post("/execute", status_code=201)
async def execute(request: SubmissionCreate):
    """
    Requests the executor to schedule execution
    """
    # Create task so we can immediate return success so frontend can show "Submission posted"
    asyncio.create_task(executor.entry(request))


@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "message": "Engine service is running"}
