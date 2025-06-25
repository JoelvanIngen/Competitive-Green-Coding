from typing import Annotated

from fastapi import APIRouter, Query
from sqlmodel import select

from common.schemas import AddProblemRequestDev, ProblemDetailsResponse, SubmissionMetadata
from db.api.modules import actions, actions_dev
from db.models.db_schemas import UserEntry
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


# WARNING: for development purposes only
@router.get("/dev/users")
async def read_users(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=1000)] = 1000
) -> list[UserEntry]:
    """Development GET endpoint to retrieve entire UserEntry table.
    WARNING: FOR DEVELOPMENT PURPOSES ONLY.

    Args:
        session (SessionDep): session to communicate with the database
        offset (int, optional): table index to start from. Defaults to 0.
        limit (Annotated[int, Query, optional): number of entries to retrieve.
            Defaults to 1000)]=1000.

    Returns:
        list[UserEntry]: entries retrieved from UserEntry table
    """

    # TODO: We should put this is a 'testing' submodule if we want to keep this
    #       or even better, put this as a standard test function in tests/unit/api/endpoints.py

    users = session.exec(select(UserEntry).offset(offset).limit(limit)).all()
    return list(users)


@router.get("/dev/submission")
async def read_submissions(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
) -> list[SubmissionMetadata]:
    """Development GET endpoint to retrieve entire SubmissionEntry table.
    WARNING: FOR DEVELOPMENT PURPOSES ONLY.

    Args:
        session (SessionDep): session to communicate with the database
        offset (int, optional): table index to start from. Defaults to 0.
        limit (Annotated[int, Query, optional): number of entries to retrieve.
            Defaults to 1000)]=1000.

    Returns:
        list[SubmissionEntry]: entries retrieved from SubmissionEntry table
    """

    return actions.read_submissions(session, offset, limit)
