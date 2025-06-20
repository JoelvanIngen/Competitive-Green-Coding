"""
Module containing API endpoints and routing logic.
- Should perform as little action as possible
- All endpoint functions should call an identically-named function from the `actions` submodule,
  to keep this file's footprint as small as possible (otherwise you'll be scrolling for half an
  hour just trying to find a specific function)
"""

from typing import Annotated

from fastapi import APIRouter, Header, Query
from sqlmodel import select
from starlette.responses import StreamingResponse

from common.schemas import (
    AddProblemRequest,
    LeaderboardRequest,
    LeaderboardResponse,
    LoginRequest,
    ProblemDetailsResponse,
    RegisterRequest,
    SubmissionCreate,
    SubmissionMetadata,
    TokenResponse,
    UserGet,
)
from db.api.modules import actions
from db.models.db_schemas import UserEntry
from db.typing import SessionDep

router = APIRouter()


def code_handler(code: str) -> None:
    raise NotImplementedError(code)  # Use variable code so pylint doesn't warn


@router.post("/auth/register")
async def register_user(user: RegisterRequest, session: SessionDep) -> TokenResponse:
    """POST endpoint to register a user and insert their data into the database.
    Produces uuid for user and stores hashed password.

    Args:
        user (RegisterRequest): data of user to be registered
        session (SessionDep): session to communicate with the database

    Raises:
        HTTPException: 403 if username of to be registered user is already in use

    Returns:
        TokenResponse: JSON Web Token of newly created user
    """

    return actions.register_user(session, user)


@router.post("/auth/login")
async def login_user(login: LoginRequest, session: SessionDep) -> TokenResponse:
    """POST endpoint to check login credentials and hand back JSON Web Token used to identify user
    in other processes.

    Args:
        login (LoginRequest): login data of user
        session (SessionDep): session to communicate with the database

    Raises:
        HTTPException: 401 if user is incorrect or password does not match password on file
        HTTPException: 422 if username does not match username constraints

    Returns:
        TokenResponse: JSON Web Token used to identify user in other processes
    """

    return actions.login_user(session, login)


@router.get("/framework")
async def get_framework(submission: SubmissionCreate):
    buff = await actions.get_framework(submission)

    # Something random here, has no further meaning
    filename = f"framework_{submission.language.name}"

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "application/gzip",
        "Content-Length": str(buff.getbuffer().nbytes),
    }
    return StreamingResponse(buff, headers=headers)


@router.post("/users/me")
async def lookup_current_user(token: TokenResponse, session: SessionDep) -> UserGet:
    """POST endpoint to get user back from input JSON Web Token.

    Args:
        token (TokenResponse): JSON Web Token of user
        session (SessionDep): session to communicate with the database

    Raises:
        HTTPException: 403 if token was invalid/expired/other error occured

    Returns:
        UserGet: user data corresponding to token
    """

    return actions.lookup_current_user(session, token)


# WARNING: for development purposes only
@router.get("/users")
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


@router.get("/leaderboard")
async def get_leaderboard(
    session: SessionDep, board_request: LeaderboardRequest
) -> LeaderboardResponse:
    return actions.get_leaderboard(session, board_request)


@router.post("/problems")
async def create_problem(problem: AddProblemRequest, session: SessionDep, authorization) -> None:
    """POST endpoint to insert problem in database.
    Produces incrementing problem_id.

    Args:
        problem (AddProblemRequest): data of problem to be inserted into the database
        session (SessionDep): session to communicate with the database

    Returns:
        None
    """

    actions.create_problem(session, problem, authorization)


@router.get("/problems")
async def read_problems(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
) -> list[ProblemDetailsResponse]:
    """Development GET endpoint to retrieve entire ProblemEntry table.
    WARNING: FOR DEVELOPMENT PURPOSES ONLY.

    Args:
        session (SessionDep): session to communicate with the database
        offset (int, optional): table index to start from. Defaults to 0.
        limit (Annotated[int, Query, optional): number of entries to retrieve.
            Defaults to 1000)]=1000.

    Returns:
        list[ProblemEntry]: entries retrieved from ProblemEntry table
    """

    return actions.read_problems(session, offset, limit)


@router.get("/problems/{problem_id}")
async def read_problem(problem_id: int, session: SessionDep) -> ProblemDetailsResponse:
    """GET endpoint to quickly get problem by problem_id.

    Args:
        problem_id (str): problem_id of problem
        session (SessionDep): session to communicate with the database

    Raises:
        HTTPException: 404 if problem with problem_id is not found

    Returns:
        ProblemDetailsResponse: problem data of problem corresponding to the problem_id
    """

    return actions.read_problem(session, problem_id)


@router.post("/submission")
async def create_submission(
    submission: SubmissionCreate, session: SessionDep
) -> SubmissionMetadata:
    """POST endpoint to create entry in SubmissionEntry table.
    Produces incrementing submission id (sid) to count the number of submissions a user has done
    for this problem.

    Args:
        submission (SubmissionPost): data of submission to be inserted into the database
        session (SessionDep): session to communicate with the database

    Returns:
        SubmissionMetadata: submission entry in the database
    """

    return actions.create_submission(session, submission)


@router.get("/submission")
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


@router.get("/health", status_code=200)
async def health_check():
    """GET endpoint to check health of the database microservice.

    Returns:
        dict[str, str]: status and corresponding message of database microservice
    """

    return {"status": "ok", "message": "DB service is running"}


@router.post("/admin/add-problem")
async def add_problem(
    problem: AddProblemRequest,
    session: SessionDep,
    authorization: str = Header(...),
) -> ProblemDetailsResponse:
    """POST endpoint to add a problem as an admin.
    Args:
        authorization (str): Authorization header containing the admin token
        session (SessionDep): session to communicate with the database
        problem (ProblemPost): data of problem to be inserted into the database
    Returns:
        ProblemGet: problem data of the newly created problem
    """

    return actions.create_problem(session, problem, authorization)
