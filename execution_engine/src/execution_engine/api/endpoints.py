from fastapi import APIRouter

from execution_engine.core import Executor
from execution_engine.models.schemas import ExecuteRequest

router = APIRouter()
executor = Executor()


@router.post("/execute")
async def execute(request: ExecuteRequest):
    # TODO: Execute submission and store results in DB
    _res = await executor.execute_code(request)  # noqa
    pass
