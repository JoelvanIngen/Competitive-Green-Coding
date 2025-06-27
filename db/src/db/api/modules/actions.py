"""
Direct entrypoint for endpoints.py.
- This module should not see/pass/parse/process DB models.
- This function should call functions from the `db.engine.ops` submodule
  Not directly from the `db.engine.queries` submodule!
- Should raise HTTPExceptions when something is going wrong
"""

from datetime import timedelta
from typing import Callable, Dict
from uuid import UUID

import jwt
from fastapi import HTTPException
from loguru import logger
from sqlmodel import Session
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool

from common.auth import check_email, check_username, data_to_jwt, jwt_to_data
from common.schemas import (
    AddProblemRequest,
    LeaderboardRequest,
    LeaderboardResponse,
    LoginRequest,
    ProblemDetailsResponse,
    ProblemsListResponse,
    RegisterRequest,
    RemoveProblemResponse,
    SettingUpdateRequest,
    SubmissionCreate,
    SubmissionFull,
    SubmissionIdentifier,
    SubmissionMetadata,
    SubmissionResult,
    TokenResponse,
    UserGet,
    UserProfileResponse,
)
from common.typing import Difficulty, PermissionLevel
from db import settings, storage
from db.engine import ops
from db.engine.ops import InvalidCredentialsError
from db.engine.queries import DBCommitError, DBEntryNotFoundError, SubmissionNotReadyError
from db.models.convert import (
    create_submission_retrieve_request,
    db_user_to_user,
    user_to_jwtokendata,
)
from db.storage import io, paths

update_handlers: Dict[str, Callable[[Session, UUID, str], UserGet]] = {
    "username": ops.update_user_username,
    "avatar_id": ops.update_user_avatar,
    "password": ops.update_user_pwd,
    "private": ops.update_user_private,
}


def _require_admin(authorization: str):
    """
    Ensures the authorization string corresponds to an admin user. Only returns if user is admin
    :returns: None
    :raises HTTPException 401: Unauthorized
    """

    try:
        permission_level = jwt_to_data(
            authorization, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        ).permission_level
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        raise HTTPException(status_code=401, detail="ERROR_UNAUTHORIZED") from e

    if permission_level != PermissionLevel.ADMIN:
        raise HTTPException(status_code=401, detail="ERROR_UNAUTHORIZED")


def update_user(s: Session, user_update: SettingUpdateRequest, token: str) -> TokenResponse:
    """Update user settings in the database.

    Args:
        s (Session): session to communicate with the database
        user_update (SettingUpdateRequest): update request to update field in database
        token (str): JSON Web Token of the user

    Raises:
        HTTPException: 401 if user has an invalid uuid
        HTTPException: 404 if user is not found
        HTTPException: 422 if the JWT is invalid

    Returns:
        TokenResponse: updated JWT of the user
    """
    if ops.try_get_user_by_uuid(s, UUID(user_update.user_uuid)) is None:
        raise HTTPException(status_code=404, detail="ERROR_USER_NOT_FOUND")

    token_data = jwt_to_data(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
    if token_data.uuid != user_update.user_uuid:
        raise HTTPException(status_code=401, detail="PROB_INVALID_UUID")

    handler = update_handlers.get(user_update.key)
    if not handler:
        raise HTTPException(status_code=422, detail="PROB_INVALID_KEY")

    user_get = handler(s, UUID(user_update.user_uuid), user_update.value)

    jwt_token = data_to_jwt(
        user_to_jwtokendata(user_get),
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM,
    )
    return TokenResponse(access_token=jwt_token)


def create_problem(
    s: Session, problem: AddProblemRequest, authorization: str
) -> ProblemDetailsResponse:
    """Create a new problem. First check if client had admin permissions and check if problem is
    valid before creating it in the database.

    Args:
        s (Session): session to communicate with the database
        problem (AddProblemRequest): problem to add to the database
        authorization (str): jwt of the client trying to create the problem

    Raises:
        HTTPException: 400 if problem is not valid
        HTTPException: 401 if user is not authorised

    Returns:
        ProblemDetailsResponse: full information about problem
    """

    _require_admin(authorization)

    if problem.difficulty not in Difficulty.to_list() or not problem.name:
        raise HTTPException(
            status_code=400,
            detail="ERROR_VALIDATION_FAILED",
        )

    return ops.create_problem(s, problem)


def remove_problem(s: Session, problem_id: int, authorization: str) -> RemoveProblemResponse:
    """Remove problem from database if client has admin permissions.

    Args:
        s (Session): session to communicate with the database
        problem_id (int): problem id of problem to remove from database
        authorization (str): jwt of the client trying to remove the problem

    Raises:
        HTTPException: 400 if problem id is not valid
        HTTPException: 404 if problem is not found
        HTTPException: 500 if there is an internal server error within the database

    Returns:
        RemoveProblemResponse: remove problem response
    """
    _require_admin(authorization)

    if problem_id <= 0:
        raise HTTPException(status_code=400, detail="ERROR_PROBLEM_VALIDATION_FAILED")

    try:
        return ops.remove_problem(s, problem_id)
    except DBEntryNotFoundError as exc:
        raise HTTPException(status_code=404, detail="ERROR_PROBLEM_NOT_FOUND") from exc
    except DBCommitError as exc:
        raise HTTPException(status_code=500, detail="ERROR_INTERNAL_SERVER_ERROR") from exc


def create_submission(s: Session, submission: SubmissionCreate) -> SubmissionIdentifier:
    """Create submission entry in the database and save code on disk. First check if problem even
    exists.

    Args:
        s (Session): session to communicate to the database
        submission (SubmissionCreate): user submission to commit

    Raises:
        HTTPException: 404 if problem is not found

    Returns:
        SubmissionIdentifier: identifier of the submission in the database
    """
    if ops.try_get_problem(s, submission.problem_id) is None:
        raise HTTPException(status_code=404, detail="ERROR_PROBLEM_NOT_FOUND")

    return ops.create_submission(s, submission)


def update_submission(s: Session, submission_result: SubmissionResult) -> SubmissionMetadata:
    """Update submission with results from execution engine.

    Args:
        s (Session): session to communicate to the database
        submission_result (SubmissionResult): results from execution engine

    Raises:
        HTTPException: 404 if submission is not found (from downstream)

    Returns:
        SubmissionMetadata: full submission metadata
    """
    return ops.update_submission(s, submission_result)


def get_submission(s: Session, problem_id: int, user_uuid: UUID) -> SubmissionFull:
    """Get submission from disk using the id of the problem to which the submission belongs and the
    uuid of the author of the submission.

    Args:
        s (Session): session to communicate with the database
        problem_id (int): id of the problem to which the submission belongs
        user_uuid (UUID): uuid of the user which made the submission

    Raises:
        HTTPException: 404 if the problem could not be found in the database
        HTTPException: 404 if the submission could not be found in the database
        HTTPException: 404 if the submission code could not be found in the storage

    Returns:
        SubmissionFull: last submission made for problem with problem_id by user with user_uuid
    """
    problem = ops.try_get_problem(s, problem_id)

    if problem is None:
        raise HTTPException(status_code=404, detail="ERROR_PROBLEM_NOT_FOUND")

    request = create_submission_retrieve_request(problem_id, user_uuid, problem.language)

    try:
        result = ops.get_submission_from_retrieve_request(s, request)
    except DBEntryNotFoundError as e:
        raise HTTPException(status_code=404, detail="ERROR_SUBMISSION_ENTRY_NOT_FOUND") from e
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="ERROR_SUBMISSION_CODE_NOT_FOUND") from e

    return result


def get_submission_result(
    s: Session, submission: SubmissionIdentifier, token: str
) -> SubmissionResult:
    """Get submission result from the database.

    Args:
        s (Session): session to communicate with the database
        submission (SubmissionIdentifier): submission identifier of the result to retrieve
        token (str): token of the user which tries to retrieve it

    Raises:
        HTTPException: 202 if the submission is not yet ready
        HTTPException: 404 if the submission entry is not found

    Returns:
        SubmissionResult: submission result from database
    """

    token_data = jwt_to_data(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
    submission_uuid = submission.submission_uuid

    try:
        result = ops.get_submission_result(s, submission_uuid, UUID(token_data.uuid))
    except DBEntryNotFoundError as e:
        raise HTTPException(status_code=404, detail="ERROR_SUBMISSION_ENTRY_NOT_FOUND") from e
    except SubmissionNotReadyError as e:
        raise HTTPException(status_code=202, detail="SUBMISSION_NOT_READY") from e
    return result


def get_leaderboard(s: Session, board_request: LeaderboardRequest) -> LeaderboardResponse:
    """Get leaderboard from the database.

    Args:
        s (Session): session to communicate with the database
        board_request (LeaderboardRequest): request of which leaderboard to retrieve

    Raises:
        HTTPException: 400 if no problems are found

    Returns:
        LeaderboardResponse: leaderboard from the database
    """
    try:
        result = ops.get_leaderboard(s, board_request)
    except DBEntryNotFoundError as exc:
        raise HTTPException(status_code=400, detail="ERROR_NO_PROBLEMS_FOUND") from exc

    if result is None:
        raise HTTPException(status_code=400, detail="ERROR_NO_PROBLEMS_FOUND")

    return result


async def get_framework_streamer(submission: SubmissionCreate):
    """
    Creates a framework archive in a non-blocking way.
    Returns a tuple containing:
    1. An async generator that yields chunks of the archive
    2. A background task to clean up resources
    """

    buff = await run_in_threadpool(storage.tar_full_framework, submission)
    return buff, BackgroundTask(buff.close)


def login_user(s: Session, login: LoginRequest) -> TokenResponse:
    """
    Logs in a user and returns a TokenResponse.
    :raises HTTPException 401: On invalid credentials.
    :raises HTTPException 422: PROB_USERNAME_CONSTRAINTS if username does not match constraints
    """

    if check_username(login.username) is False:
        raise HTTPException(status_code=422, detail="PROB_USERNAME_CONSTRAINTS")

    user_get = ops.try_login_user(s, login)

    if user_get is None:
        raise HTTPException(status_code=401, detail="ERROR_INVALID_LOGIN")

    jwt_token = data_to_jwt(
        user_to_jwtokendata(user_get),
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM,
    )
    return TokenResponse(access_token=jwt_token)


def lookup_current_user(s: Session, token: str) -> UserGet:
    """Look up the current user.

    Args:
        s (Session): session to communicate with the database
        token (str): token to get user from

    Raises:
        HTTPException: 401 if token was invalid/expired error occured
        HTTPException: 404 if user is not found
        HTTPException: 411 if password is incorrect
        HTTPException: 500 if an unexpected error has occured

    Returns:
        UserGet: user data corresponding to token
    """

    try:
        jwtokendata = jwt_to_data(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        user_entry = ops.try_get_user_by_uuid(s, UUID(jwtokendata.uuid))

        if user_entry is None:
            raise HTTPException(status_code=404, detail="ERROR_USER_NOT_FOUND")

        return db_user_to_user(user_entry)

    except jwt.ExpiredSignatureError as e:
        raise HTTPException(401, "ERROR_TOKEN_EXPIRED") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(401, "ERROR_TOKEN_INVALID") from e
    except InvalidCredentialsError as e:
        raise HTTPException(411, "ERROR_INVALID_USERNAME_OR_PASSWORD_COMBINATION") from e
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(500, "ERROR_INTERNAL_SERVER_ERROR") from e


def lookup_user(s: Session, username: str) -> UserGet:
    """Lookup user in the databse.

    Args:
        s (Session): session to communicate with the database
        username (str): username to get user from

    Raises:
        HTTPException: 404 if user is not found

    Returns:
        UserGet: data of user with username
    """
    try:
        return ops.get_user_from_username(s, username)
    except DBEntryNotFoundError as e:
        raise HTTPException(404, "ERROR_USERNAME_NOT_FOUND") from e


def read_problem(s: Session, problem_id: int, token: str) -> ProblemDetailsResponse:
    """Retrieve problem from the database with corresponding template code. If user has made a
    previous submission for this problem, this code will be loaded instead of the template code.

    Args:
        s (Session): session to communicate with the database
        problem_id (int): id of the problem
        token (str): JWT of the user

    Raises:
        HTTPException: 404 if problem is not found

    Returns:
        ProblemDetailsResponse: problem data of problem corresponding to the problem_id
    """

    try:
        problem = ops.read_problem(s, problem_id)
    except DBEntryNotFoundError as e:
        raise HTTPException(404, detail="ERROR_PROBLEM_NOT_FOUND") from e

    token_data = jwt_to_data(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

    request = create_submission_retrieve_request(
        problem_id,
        UUID(token_data.uuid),
        problem.language,
    )

    try:
        submission = ops.get_submission_from_retrieve_request(s, request)
        problem.submission_code = submission.code
        problem.submission_uuid = submission.submission_uuid
    except DBEntryNotFoundError:
        return problem
    except FileNotFoundError:
        return problem

    return problem


def read_problems(s: Session, offset: int, limit: int) -> list[ProblemDetailsResponse]:
    """Read multiple problems from the database.

    Args:
        s (Session): session to communicate with the database
        offset (int): index to start from
        limit (int): number of entries to get

    Returns:
        list[ProblemDetailsResponse]: list of problems
    """
    return ops.read_problems(s, offset, limit)


def get_problem_metadata(s: Session, offset: int, limit: int) -> ProblemsListResponse:
    """Get metadata for the problems.

    Args:
        s (Session): session to communicate with the database
        offset (int): index to start from
        limit (int): number of entries to get

    Raises:
        HTTPException: 404 if no problems are found

    Returns:
        ProblemsListResponse: list of problems
    """
    if offset < 0 or limit <= 0 or limit > 100:
        raise HTTPException(status_code=404, detail="ERROR_NO_PROBLEMS_FOUND")

    result = ops.get_problem_metadata(s, offset, limit)

    if result is None or result.total == 0:
        raise HTTPException(status_code=404, detail="ERROR_NO_PROBLEMS_FOUND")

    return result


def read_submissions(s: Session, offset: int, limit: int) -> list[SubmissionMetadata]:
    """Read submissions from database.

    Args:
        s (Session): session to communicate with the database
        offset (int): index to start from
        limit (int): number of entries to get

    Returns:
        list[SubmissionMetadata]: list of submissions
    """
    return ops.get_submissions(s, offset, limit)


def register_user(s: Session, user: RegisterRequest) -> TokenResponse:
    """Register user to the database.

    Args:
        s (Session): session to communicate with the database
        user (RegisterRequest): user to register

    Raises:
        HTTPException: 409 if username is in use
        HTTPException: 409 if email is in use
        HTTPException: 422 if username does not match constraints
        HTTPException: 422 if email does not match constraints

    Returns:
        TokenResponse: jwt of newly created user
    """

    if check_email(user.email) is False:
        raise HTTPException(status_code=422, detail="PROB_INVALID_EMAIL")

    if check_username(user.username) is False:
        raise HTTPException(status_code=422, detail="PROB_USERNAME_CONSTRAINTS")

    if ops.check_unique_username(s, user.username) is False:
        raise HTTPException(status_code=409, detail="PROB_USERNAME_EXISTS")

    if ops.check_unique_email(s, user.email) is False:
        raise HTTPException(status_code=409, detail="PROB_EMAIL_REGISTERED")

    user_get = ops.register_new_user(s, user)
    jwt_token = data_to_jwt(
        user_to_jwtokendata(user_get),
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM,
    )

    return TokenResponse(access_token=jwt_token)


async def store_submission_code(submission: SubmissionCreate) -> None:
    """Store submission code on disk.

    Args:
        submission (SubmissionCreate): submission of the user
    """
    io.write_file(
        submission.code,
        paths.submission_code_path(submission),
        filename="submission.c",
    )


def change_user_permission(
    s: Session, username: str, permission: PermissionLevel, authorization: str
) -> UserGet:
    """Change permission of user with username.

    Args:
        s (Session): session to communicate with the database
        username (str): username of the user to update permissions
        permission (PermissionLevel): permission level of the user
        authorization (str): jwt of the client trying to update permission level

    Raises:
        HTTPException: 400 if permission is not a real permission level
        HTTPException: 401 if client is not an admin

    Returns:
        UserGet: updated user
    """
    _require_admin(authorization)

    if permission not in PermissionLevel:
        raise HTTPException(status_code=400, detail="ERROR_INVALID_PERMISSION")

    return ops.change_user_permission(s, username, permission)


def get_profile_from_username(s: Session, username: str) -> UserProfileResponse:
    """Get profile from username

    Args:
        s (Session): session to communicate with the database
        username (str): username of the user to get profile from

    Raises:
        HTTPException: 404 if user is not found or private

    Returns:
        UserProfileResponse: data to load in profile page
    """
    try:
        user_get = ops.get_user_from_username(s, username)

        if user_get.private:
            raise HTTPException(404, "ERROR_USER_NOT_FOUND")

    except DBEntryNotFoundError as e:
        raise HTTPException(404, "ERROR_USER_NOT_FOUND") from e

    avatar_id = user_get.avatar_id

    solved = ops.get_user_solved(s, user_get.uuid)
    language_stats = ops.get_user_language_stats(s, user_get.uuid)

    recent_submissions = ops.get_recent_submissions(s, user_get.uuid, n=3)

    return UserProfileResponse(
        username=username,
        avatar_id=avatar_id,
        solved=solved,
        language_stats=language_stats,
        recent_submissions=recent_submissions,
    )
