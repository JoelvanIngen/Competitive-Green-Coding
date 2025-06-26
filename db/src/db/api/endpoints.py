"""
Module containing API endpoints and routing logic.
- Should perform as little action as possible
- All endpoint functions should call an identically-named function from the `actions` submodule,
  to keep this file's footprint as small as possible (otherwise you'll be scrolling for half an
  hour just trying to find a specific function)
"""

from uuid import UUID

from fastapi import APIRouter, Header
from starlette.responses import StreamingResponse

from common.schemas import (
    AddProblemRequest,
    ChangePermissionRequest,
    LeaderboardRequest,
    LeaderboardResponse,
    LoginRequest,
    ProblemAllRequest,
    ProblemDetailsResponse,
    ProblemsListResponse,
    RegisterRequest,
    RemoveProblemRequest,
    RemoveProblemResponse,
    SettingUpdateRequest,
    SubmissionCreate,
    SubmissionIdentifier,
    SubmissionFull,
    SubmissionResult,
    TokenResponse,
    UserGet,
)
from db.api.modules import actions
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


@router.put("/settings")
async def update_user(
    user: SettingUpdateRequest,
    session: SessionDep,
    authorization: str = Header(..., alias="Authorization"),
) -> TokenResponse:
    """POST endpoint to update user information and hand back a JSON Web Token used to identify
    user to the clientside.

    Args:
        user (SettingUpdateRequest): schema used for updating user information.
        session (SessionDep): session to communicate with the database

    Raises:
        HTTPException(status_code=404, detail="ERROR_USER_NOT_FOUND")
        HTTPException(status_code=422, detail="PROB_INVALID_KEY")

    Returns:
        TokenResponse: JSON Web Token used to identify user in other processes
    """
    parts = authorization.split()
    token = parts[1]

    return actions.update_user(session, user, token)


@router.post("/framework")
async def engine_request_framework(submission: SubmissionCreate):
    # Something random here, has no further meaning
    filename = f"framework_{submission.language.name}"

    streamer, cleanup_task = await actions.get_framework_streamer(submission)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "application/gzip",
    }
    return StreamingResponse(streamer, headers=headers, background=cleanup_task)


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


@router.post("/leaderboard")
async def get_leaderboard(
    session: SessionDep, board_request: LeaderboardRequest
) -> LeaderboardResponse:
    return actions.get_leaderboard(session, board_request)


@router.post("/problems/all")
async def get_all_problems(
    session: SessionDep,
    request: ProblemAllRequest,
) -> ProblemsListResponse:
    return actions.get_problem_metadata(session, offset=0, limit=request.limit or 100)


@router.get("/problems/{problem_id}")
async def read_problem(
    problem_id: int,
    session: SessionDep,
    authorization: str = Header(...),
) -> ProblemDetailsResponse:
    """GET endpoint to retrieve problem from the database with corresponding template code. If user
    has made a previous submission for this problem, this code will be loaded instead of the
    template code.

    Args:
        problem_id (str): problem_id of problem
        session (SessionDep): session to communicate with the database

    Raises:
        HTTPException: 404 if problem with problem_id is not found

    Returns:
        ProblemDetailsResponse: problem data of problem corresponding to the problem_id
    """

    return actions.read_problem(session, problem_id, authorization)


@router.post("/submission")
async def create_submission(
    submission: SubmissionCreate, session: SessionDep, authorization: str = Header(...)
) -> SubmissionIdentifier:
    """POST endpoint to create entry in SubmissionEntry table.
    Produces incrementing submission id (sid) to count the number of submissions a user has done
    for this problem.

    Args:
        submission (SubmissionPost): data of submission to be inserted into the database
        session (SessionDep): session to communicate with the database

    Returns:
        SubmissionMetadata: submission entry in the database
    """

    del authorization

    return actions.create_submission(session, submission)


@router.get("/submission/{problem_id}/{user_uuid}")
async def get_submission(problem_id: int, user_uuid: UUID, session: SessionDep) -> SubmissionFull:
    """GET endpoint to get most recent submission for problem with problem_id by user with
    user_uuid.

    Args:
        problem_id (int): problem id of problem submission was for
        user_uuid (UUID): user id of author of the submission
        session (SessionDep): session to communicate with the database

    Returns:
        SubmissionFull: all data belonging to most recent submission made by user with uuid for
            problem with problem_id
    """

    return actions.get_submission(session, problem_id, user_uuid)


@router.post("/write-submission-result", status_code=201)
async def write_submission_results(
    session: SessionDep, submission_result: SubmissionResult
) -> None:
    """POST endpoint to append submission result to a submission entry.
    This is used to append the result of a submission to the existing submission entry.

    Args:
        session (SessionDep): session to communicate with the database
        submission_result (SubmissionResult): data of submission result to be appended

    Raises:
        HTTPException: 404 if submission with submission_uuid is not found

    Returns:
        None
    """

    actions.update_submission(session, submission_result)


@router.post("/submission-result")
async def get_submission_result(
    session: SessionDep,
    submission: SubmissionIdentifier,
    authorization: str = Header(..., alias="Authorization"),
) -> SubmissionResult:

    return actions.get_submission_result(session, submission, authorization)


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
    """
    POST endpoint to add a problem as an admin.

    Args:
        authorization (str): Authorization header containing the admin token
        session (SessionDep): session to communicate with the database
        problem (ProblemPost): data of problem to be inserted into the database
    Returns:
        ProblemGet: problem data of the newly created problem
    """

    return actions.create_problem(session, problem, authorization)


@router.post("/admin/change-permission")
async def change_user_permission(
    session: SessionDep,
    request: ChangePermissionRequest,
    authorization: str = Header(...),
) -> UserGet:
    """
    POST endpoint to change user permission level as an admin.

    Args:
        username (str): username of user whose permission level is to be changed
        permissionlevel (PermissionLevel): new permission level for the user
        authorization (str): Authorization header containing the admin tokentoken
    """

    return actions.change_user_permission(
        session, request.username, request.permission_level, authorization
    )


@router.post("/admin/remove-problem")
async def remove_problem(
    request: RemoveProblemRequest,
    session: SessionDep,
    authorization: str = Header(...),
) -> RemoveProblemResponse:
    return actions.remove_problem(session, request.problem_id, authorization)
