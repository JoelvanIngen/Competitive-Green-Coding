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
    SubmissionFull,
    SubmissionIdentifier,
    SubmissionResult,
    TokenResponse,
    UserGet,
    UserProfileResponse,
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
        HTTPException: 409 if username is in use
        HTTPException: 409 if email is in use
        HTTPException: 422 if username does not match constraints
        HTTPException: 422 if email does not match constraints


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
    """PUT endpoint to update user information and hand back a JSON Web Token used to identify
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
    token = authorization.split()[1]

    return actions.update_user(session, user, token)


@router.get("/settings")
async def get_user_information(
    session: SessionDep, authorization: str = Header(..., alias="Authorization")
) -> UserGet:
    """GET endpoint to get user back from input JSON Web Token.

    Args:
        token (TokenResponse): JSON Web Token of user
        session (SessionDep): session to communicate with the database

    Raises:
        HTTPException: 401 if token was invalid/expired error occured
        HTTPException: 404 if user is not found
        HTTPException: 411 if password is incorrect
        HTTPException: 500 if an unexpected error has occured

    Returns:
        UserGet: user data corresponding to token
    """

    token = authorization.split()[1]
    return actions.lookup_current_user(session, token)


@router.post("/framework")
async def engine_request_framework(submission: SubmissionCreate) -> StreamingResponse:
    """POST endpoint to get framework from disk.

    Args:
        submission (SubmissionCreate): submission which was created

    Returns:
        StreamingResponse: framework
    """
    filename = f"framework_{submission.language.name}"

    streamer, cleanup_task = await actions.get_framework_streamer(submission)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "application/gzip",
    }
    return StreamingResponse(streamer, headers=headers, background=cleanup_task)


@router.post("/leaderboard")
async def get_leaderboard(
    session: SessionDep, board_request: LeaderboardRequest
) -> LeaderboardResponse:
    """POST endpoint to get the leaderboard.

    Args:
        session (SessionDep): session to communicate with the database
        board_request (LeaderboardRequest): request to get leaderboard

    Raises:
        HTTPException: 400 if no problems are found

    Returns:
        LeaderboardResponse: leaderboard from the database
    """
    return actions.get_leaderboard(session, board_request)


@router.post("/problems/all")
async def get_all_problems(
    session: SessionDep,
    request: ProblemAllRequest,
) -> ProblemsListResponse:
    """POST endpoint to get all problems from database.

    Args:
        session (SessionDep): session to communicate with the database
        request (ProblemAllRequest): request to get problems from the database

    Raises:
        HTTPException: 404 if no problems are found

    Returns:
        ProblemsListResponse: list of problems
    """
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

    Raises:
        HTTPException: 404 if problem is not found

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

    Raises:
        HTTPException: 404 if the problem could not be found in the database
        HTTPException: 404 if the submission could not be found in the database
        HTTPException: 404 if the submission code could not be found in the storage

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
    """POST endpoint to get submission result from the database.

    Args:
        session (SessionDep): session to communicate with the database
        submission (SubmissionIdentifier): submission to get result from
        authorization (str, optional): authorization token.
            Defaults to Header(..., alias="Authorization").

    Raises:
        HTTPException: 202 if the submission is not yet ready
        HTTPException: 404 if the submission entry is not found

    Returns:
        SubmissionResult: submission result from database
    """

    return actions.get_submission_result(session, submission, authorization)


@router.get("/profile/{username}")
async def get_profile_from_username(session: SessionDep, username: str) -> UserProfileResponse:
    """GET endpoint to get profile from username.

    Args:
        session (SessionDep): session to communicate with the database
        username (str): username to get profile from

    Raises:
        HTTPException: 404 if user is not found or private

    Returns:
        UserProfileResponse: data to load in profile page
    """
    return actions.get_profile_from_username(session, username)


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

    Raises:
        HTTPException: 400 if problem is not valid
        HTTPException: 401 if user is not authorised

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

    Raises:
        HTTPException: 400 if permission is not a real permission level
        HTTPException: 401 if client is not an admin

    Returns:
        UserGet: updated user
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
    """POST endpoint to remove problem from the database.

    Args:
        request (RemoveProblemRequest): request to remove problem.
        session (SessionDep): session to communicate with the database
        authorization (str, optional): authorization token. Defaults to Header(...).

    Raises:
        HTTPException: 400 if problem id is not valid
        HTTPException: 404 if problem is not found
        HTTPException: 500 if there is an internal server error within the database

    Returns:
        RemoveProblemResponse: remove problem response
    """

    return actions.remove_problem(session, request.problem_id, authorization)
