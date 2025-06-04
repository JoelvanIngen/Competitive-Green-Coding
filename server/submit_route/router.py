from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# Import necessary modules from the execution engine
from execution_engine.src.core.executor import Executor
from execution_engine.src.models.schemas import ExecuteRequest, ExecuteResult

# Create a new API router
router = APIRouter()
executor = Executor()

# Request model for frontend
class submission_code(BaseModel):
    code: str

# Response model for frontend
class result_code(BaseModel):
    status: str
    output: Optional[str]
    cpu_time_ms: Optional[int]

# Endpoint to submit code for execution
@router.post("/submit-code", response_model=result_code)
async def submit_code(submission: submission_code):
    request = ExecuteRequest(code=submission.code)

    # Validate the request
    try:
        result_dict = await executor.execute_code(request)
        result = ExecuteResult(**result_dict)

        return result_code(
            status=result.status,
            output=result.error_msg if result.status != "success" else None,
            cpu_time_ms=result.runtime_ms
        )

    except Exception as e:
        raise HTTPException(500, detail=f"failed: {str(e)}")

