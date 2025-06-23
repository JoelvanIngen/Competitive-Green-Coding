"""
Direct entrypoint for endpoints.py.
- This module should not see/pass/parse/process DB models.
- This function should call functions from the `db.engine.ops` submodule
  Not directly from the `db.engine.queries` submodule!
- Should raise HTTPExceptions when something is going wrong
"""

import os
from datetime import timedelta

import jwt
from fastapi import HTTPException
from loguru import logger
from sqlmodel import Session

from common.auth import check_email, check_username, data_to_jwt, jwt_to_data
from common.schemas import (
    AddProblemRequest,
    LeaderboardRequest,
    LeaderboardResponse,
    LoginRequest,
    ProblemDetailsResponse,
    ProblemsListResponse,
    RegisterRequest,
    SubmissionCreate,
    SubmissionMetadata,
    TokenResponse,
    UserGet,
)
from common.typing import Difficulty, PermissionLevel
from db import settings, storage
from db.engine import ops
from db.engine.ops import InvalidCredentialsError
from db.engine.queries import DBEntryNotFoundError
from db.models.convert import user_to_jwtokendata
from db.storage import io, paths


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))

WRAPPER_BASE_PATH = os.path.join(PROJECT_ROOT, "storage-example", "wrappers")


def create_wrapper(problem: AddProblemRequest, problem_id: int) -> None:
    wrapper_location = f"{problem_id}/{problem.language.info.name}"
    wrapper_location = f"{wrapper_location}.{problem.language.info.file_extension}"

    filepath = os.path.join(WRAPPER_BASE_PATH, wrapper_location)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w") as f:
        f.write(problem.wrapper)

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=500,
            detail="ERROR_CANNOT_CREATE_WRAPPER",
        )


def create_problem(
    s: Session, problem: AddProblemRequest, authorization: str
) -> ProblemDetailsResponse:

    try:
        permission_level = jwt_to_data(
            authorization, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        ).permission_level
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="ERROR_UNAUTHORIZED") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="ERROR_UNAUTHORIZED") from e

    if permission_level != PermissionLevel.ADMIN:
        raise HTTPException(status_code=401, detail="ERROR_UNAUTHORIZED")

    if problem.difficulty not in Difficulty.to_list() or not problem.name:
        raise HTTPException(
            status_code=400,
            detail="ERROR_VALIDATION_FAILED",
        )

    resp = ops.create_problem(s, problem)
    create_wrapper(problem, resp.problem_id)

    return resp


def create_submission(s: Session, submission: SubmissionCreate) -> SubmissionMetadata:
    return ops.create_submission(s, submission)


def get_leaderboard(s: Session, board_request: LeaderboardRequest) -> LeaderboardResponse:
    return ops.get_leaderboard(s, board_request)


async def get_framework(submission: SubmissionCreate):
    return storage.tar_stream_generator(storage.tar_full_framework(submission))


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


def lookup_current_user(s: Session, token: TokenResponse) -> UserGet:
    """
    Looks up the current user
    :raises HTTPException 401: On expired token or on invalid token
    :raises HTTPException 500: On unexpected error
    """

    try:
        jwtokendata = jwt_to_data(
            token.access_token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        )
        return ops.get_user_from_username(s, jwtokendata.username)
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(413, "Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(412, "Unauthorized") from e
    except InvalidCredentialsError as e:
        raise HTTPException(411, "Invalid username or password") from e
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error") from e


def lookup_user(s: Session, username: str) -> UserGet:
    try:
        return ops.get_user_from_username(s, username)
    except DBEntryNotFoundError as e:
        raise HTTPException(404, "User not found") from e


def read_problem(s: Session, problem_id: int) -> ProblemDetailsResponse:
    return ops.read_problem(s, problem_id)


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
