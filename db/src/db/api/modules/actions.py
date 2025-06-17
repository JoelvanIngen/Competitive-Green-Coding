"""
Direct entrypoint for endpoints.py.
- This module should not see/pass/parse/process DB models.
- This function should call functions from the `db.engine.ops` submodule
  Not directly from the `db.engine.queries` submodule!
- Should raise HTTPExceptions when something is going wrong
"""

import jwt
from fastapi import HTTPException
from loguru import logger
from sqlmodel import Session

from common.schemas import (
    LeaderboardGet,
    ProblemGet,
    ProblemPost,
    SubmissionCreate,
    SubmissionMetadata,
    TokenResponse,
    UserGet,
    UserLogin,
    UserRegister,
)
from db.auth import check_username, data_to_jwt, jwt_to_data
from db.engine import ops
from db.engine.queries import DBEntryNotFoundError
from db.models.convert import user_to_jwtokendata
from db.storage import io, paths


def create_problem(s: Session, problem: ProblemPost) -> ProblemGet:
    return ops.create_problem(s, problem)


def create_submission(s: Session, submission: SubmissionCreate) -> SubmissionMetadata:
    return ops.create_submission(s, submission)


def get_leaderboard(s: Session) -> LeaderboardGet:
    return ops.get_leaderboard(s)


async def get_submission_code(submission: SubmissionMetadata) -> str:
    return io.read_file(
        # Hardcode C submission for now
        paths.submission_metadata_to_dir(submission),
        "submission.c",
    )


def login_user(s: Session, login: UserLogin) -> TokenResponse:
    """
    Logs in a user and returns a TokenResponse.
    :raises HTTPException 401: On invalid credentials.
    :raises HTTPException 422: PROB_USERNAME_CONSTRAINTS if username does not match constraints
    """

    if check_username(login.username) is False:
        raise HTTPException(status_code=400, detail="Username contains illegal characters")
    if len(login.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    try:
        user_get = ops.login_user(s, login)
    except HTTPException as e:
        if e.status_code == 401:
            raise HTTPException(status_code=400, detail="Invalid username or password") from e
        raise HTTPException(status_code=500, detail="An unexpected error occured") from e

    jwt_token = data_to_jwt(user_to_jwtokendata(user_get))
    return TokenResponse(access_token=jwt_token)


def lookup_current_user(s: Session, token: TokenResponse) -> UserGet:
    """
    Looks up the current user
    :raises HTTPException 401: On expired token or on invalid token
    :raises HTTPException 500: On unexpected error
    """

    try:
        jwtokendata = jwt_to_data(token.access_token)
        return ops.get_user_from_username(s, jwtokendata.username)
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(401, "Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(401, "Unauthorized") from e
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error") from e


def lookup_user(s: Session, username: str) -> UserGet:
    try:
        return ops.get_user_from_username(s, username)
    except DBEntryNotFoundError as e:
        raise HTTPException(404, "User not found") from e


def read_problem(s: Session, problem_id: int) -> ProblemGet:
    return ops.read_problem(s, problem_id)


def read_problems(s: Session, offset: int, limit: int) -> list[ProblemGet]:
    return ops.read_problems(s, offset, limit)


def read_submissions(s: Session, offset: int, limit: int) -> list[SubmissionMetadata]:
    return ops.get_submissions(s, offset, limit)


def register_user(s: Session, user: UserRegister) -> TokenResponse:
    user_get = ops.register_new_user(s, user)
    jwt_token = data_to_jwt(user_to_jwtokendata(user_get))

    return TokenResponse(access_token=jwt_token)


async def store_submission_code(submission: SubmissionCreate) -> None:
    io.write_file(
        submission.code,
        paths.submission_create_to_dir(submission),
        filename="submission.c",  # Hardcode C submission for now
    )
