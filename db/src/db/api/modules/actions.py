"""
Direct entrypoint for endpoints.py.
- This module should not see/pass/parse/process DB models.
- This function should call functions from the `db.engine.ops` submodule
  Not directly from the `db.engine.queries` submodule!
- Should raise HTTPExceptions when something is going wrong
"""

from http.client import HTTPException

import jwt
from loguru import logger
from sqlmodel import Session

from db.auth import jwt_to_user, user_to_jwt
from db.engine import ops
from db.engine.queries import DBEntryNotFoundError
from db.models.schemas import (
    LeaderboardGet,
    ProblemGet,
    ProblemPost,
    SubmissionGet,
    SubmissionPost,
    TokenResponse,
    UserGet,
    UserLogin,
    UserRegister,
)
from db.storage import io, paths


def create_problem(s: Session, problem: ProblemPost) -> None:
    ops.create_problem(s, problem)


def create_submission(s: Session, submission: SubmissionPost) -> None:
    return ops.create_submission(s, submission)


def get_leaderboard(s: Session) -> LeaderboardGet:
    return ops.get_leaderboard(s)


async def get_submission_code(submission: SubmissionPost) -> str:
    return io.read_file(
        paths.submission_post_to_dir(submission),
    )


def login_user(s: Session, login: UserLogin) -> TokenResponse:
    """
    Logs in a user and returns a TokenResponse.
    :raises HTTPException 401: On invalid credentials.
    """

    try:
        user = ops.get_user_from_username(s, login.username)
        # TODO: We should very very probably check for password too
    # except (DBEntryNotFoundError, InvalidPasswordError) as e:
    except DBEntryNotFoundError as e:
        raise HTTPException(401, "Unauthorized") from e

    jwt_token = user_to_jwt(user)
    return TokenResponse(access_token=jwt_token)


def lookup_current_user(token: TokenResponse) -> UserGet:
    """
    Looks up the current user
    :raises HTTPException 401: On expired token or on invalid token
    :raises HTTPException 500: On unexpected error
    """

    try:
        return jwt_to_user(token.access_token)
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


def read_submissions(s: Session, offset: int, limit: int) -> list[SubmissionGet]:
    return ops.get_submissions(s, offset, limit)


def register_user(s: Session, user: UserRegister) -> UserGet:
    return ops.register_new_user(s, user)


async def store_submission_code(submission: SubmissionPost) -> None:
    io.write_file(
        submission.code,
        paths.submission_post_to_dir(submission),
    )
