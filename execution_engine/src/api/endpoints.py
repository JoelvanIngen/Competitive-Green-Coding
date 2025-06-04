from fastapi import APIRouter

from execution_engine.src.core.executor import Executor
from execution_engine.src.models.schemas import ExecuteRequest

router = APIRouter()
executor = Executor()


@router.post("/execute")
async def execute(request: ExecuteRequest):
    # TODO: Execute submission and store results in DB
    res = await executor.execute_code(request)
    pass
