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

    _require_admin(authorization)

    if problem.difficulty not in Difficulty.to_list() or not problem.name:
        raise HTTPException(
            status_code=400,
            detail="ERROR_VALIDATION_FAILED",
        )

    return ops.create_problem(s, problem)


def remove_problem(s: Session, problem_id: int, authorization: str) -> RemoveProblemResponse:
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
    if ops.try_get_problem(s, submission.problem_id) is None:
        raise HTTPException(status_code=404, detail="ERROR_PROBLEM_NOT_FOUND")

    return ops.create_submission(s, submission)


def update_submission(s: Session, submission_result: SubmissionResult) -> SubmissionMetadata:
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
        raise HTTPException(status_code=401, detail="Unauthorized")

    jwt_token = data_to_jwt(
        user_to_jwtokendata(user_get),
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM,
    )
    return TokenResponse(access_token=jwt_token)


def lookup_current_user(s: Session, token: str) -> UserGet:
    """
    Looks up the current user
    :raises HTTPException 401: On expired token or on invalid token
    :raises HTTPException 500: On unexpected error
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
        problem.submission_id = submission.submission_uuid
    except DBEntryNotFoundError:
        return problem
    except FileNotFoundError:
        return problem

    return problem


def read_problems(s: Session, offset: int, limit: int) -> list[ProblemDetailsResponse]:
    return ops.read_problems(s, offset, limit)


def get_problem_metadata(s: Session, offset: int, limit: int) -> ProblemsListResponse:
    if offset < 0 or limit <= 0 or limit > 100:
        raise HTTPException(status_code=404, detail="ERROR_NO_PROBLEMS_FOUND")

    result = ops.get_problem_metadata(s, offset, limit)

    if result is None or result.total == 0:
        raise HTTPException(status_code=404, detail="ERROR_NO_PROBLEMS_FOUND")

    return result


def read_submissions(s: Session, offset: int, limit: int) -> list[SubmissionMetadata]:
    return ops.get_submissions(s, offset, limit)


def register_user(s: Session, user: RegisterRequest) -> TokenResponse:
    """
    Register a new user to the DB
    :returns: The created DB user entry
    :raises HTTPException 400: On bad username
    :raises HTTPException 409: On existing username
    :raises HTTPException 500: On DB error (from downstream)
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
    io.write_file(
        submission.code,
        paths.submission_code_path(submission),
        filename="submission.c",  # Hardcode C submission for now
    )


def change_user_permission(
    s: Session, username: str, permission: PermissionLevel, authorization: str
) -> UserGet:
    _require_admin(authorization)

    if permission not in PermissionLevel:
        raise HTTPException(status_code=400, detail="ERROR_INVALID_PERMISSION")

    return ops.change_user_permission(s, username, permission)


def get_profile_from_username(s: Session, username: str) -> UserProfileResponse:
    try:
        user_get = ops.get_user_from_username(s, username)

        if user_get.private:
            raise DBEntryNotFoundError

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
