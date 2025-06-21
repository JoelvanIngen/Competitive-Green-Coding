from fastapi import APIRouter

from common.schemas import AddProblemRequestDev, ProblemDetailsResponse
from db.api.modules import actions_dev
from db.typing import SessionDep


router = APIRouter()

@router.post("/add-problem")
async def add_problem(
    problem: AddProblemRequestDev,
    session: SessionDep,
) -> ProblemDetailsResponse:
    """
    Receives a pre-made problem that has already been created on the storage. Hardcodes the problem
    id to match that existing problem.
    """

    return actions_dev.create_problem(session, problem)