"""
Module for all high-level operations that act indirectly on the database
- Functions here do not directly use DB models, unless to pass them around or convert them
- This is only for database actions, or DB model processing. All other actions should happen
  in actions.py
- Should raise HTTPExceptions when something is going wrong
"""

from typing import cast
from uuid import UUID

from fastapi import HTTPException
from loguru import logger
from sqlmodel import Session

from common.auth import check_password, hash_password
from common.schemas import (
    AddProblemRequest,
    LeaderboardRequest,
    LeaderboardResponse,
    LoginRequest,
    ProblemDetailsResponse,
    RegisterRequest,
    SubmissionCreate,
    SubmissionMetadata,
    SubmissionResult,
    UserGet,
)
from common.typing import Difficulty
from db.engine import queries
from db.engine.queries import DBCommitError, DBEntryNotFoundError
from db.models.convert import (
    append_submission_results,
    db_problem_to_problem_get,
    db_submission_to_submission_metadata,
    db_user_to_user,
    problem_post_to_db_problem,
    submission_create_to_db_submission,
)
from db.models.db_schemas import ProblemEntry, ProblemTagEntry, UserEntry
from db.typing import DBEntry


class InvalidCredentialsError(Exception):
    """
    Invalid credentials were provided.
    """


def _commit_or_500(session, entry: DBEntry):
    """
    Attempts to commit the given entry to the database
    :raises HTTPException 500: On DB error
    """

    try:
        queries.commit_entry(session, entry)
    except DBCommitError as e:
        logger.error(f"DB commit error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


def create_problem(s: Session, problem: AddProblemRequest) -> ProblemDetailsResponse:
    problem_entry = problem_post_to_db_problem(problem)

    _commit_or_500(s, problem_entry)

    problem_id = problem_entry.problem_id
    for tag in problem.tags:
        problem_tag_entry = ProblemTagEntry(problem_id=problem_id, tag=tag)
        _commit_or_500(s, problem_tag_entry)

    problem_get = db_problem_to_problem_get(problem_entry)

    return problem_get


def create_submission(s: Session, submission: SubmissionCreate) -> SubmissionMetadata:
    submission_entry = submission_create_to_db_submission(submission)

    # TODO: Code saving in storage
    # code_handler(submission.code)

    _commit_or_500(s, submission_entry)

    return db_submission_to_submission_metadata(submission_entry)


def update_submission(s: Session, submission_result: SubmissionResult):
    try:
        submission_entry = queries.get_submission_by_sub_uuid(s, submission_result.submission_uuid)
    except DBEntryNotFoundError as e:
        raise HTTPException(status_code=404, detail="Submission entry not found") from e

    append_submission_results(submission_entry, submission_result)
    _commit_or_500(s, submission_entry)


def get_leaderboard(s: Session, board_request: LeaderboardRequest) -> LeaderboardResponse:
    return queries.get_leaderboard(s, board_request)


def get_submissions(s: Session, offset: int, limit: int) -> list[SubmissionMetadata]:
    return [
        db_submission_to_submission_metadata(entry)
        for entry in queries.get_submissions(s, offset, limit)
    ]


def get_user_from_username(s: Session, username: str) -> UserGet:
    """
    :raises DBEntryNotFoundError: If username is not found (from downstream)
    """
    return db_user_to_user(queries.get_user_by_username(s, username))


def read_problem(s: Session, problem_id: int) -> ProblemDetailsResponse:
    """
    Attempts to read the given problem from the database
    :raises HTTPException 404: Problem not found if problem not in DB
    """

    problem = queries.try_get_problem(s, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    problem = cast(ProblemEntry, problem)  # Solves type issues

    problem_get = db_problem_to_problem_get(problem)

    return problem_get


def read_problems(s: Session, offset: int, limit: int) -> list[ProblemDetailsResponse]:
    problem_entries = queries.get_problems(s, offset, limit)

    problem_gets = []
    for problem in problem_entries:
        problem_get = db_problem_to_problem_get(problem)
        problem_gets.append(problem_get)

    return problem_gets


def check_unique_username(s: Session, username: str) -> bool:
    """Checks if username of to be registered user is unique.

    Args:
        s (Session): session to communicate with the database
        username (str): username of registered user

    Returns:
        bool: if username is unique
    """
    if queries.try_get_user_by_username(s, username):
        return False
    return True


def check_unique_email(s: Session, email: str) -> bool:
    """Checks if username of to be registered user is unique.

    Args:
        s (Session): session to communicate with the database
        email (str): email of to be registered user

    Returns:
        bool: if email is unique
    """
    if queries.try_get_user_by_email(s, email):
        return False
    return True


def register_new_user(s: Session, user: RegisterRequest) -> UserGet:
    """
    Register a new user to the DB
    :raises HTTPException 500: On DB error
    """

    user_entry = UserEntry(
        username=user.username,
        email=user.email,
        permission_level=user.permission_level,
        hashed_password=hash_password(user.password),
    )

    _commit_or_500(s, user_entry)

    return db_user_to_user(user_entry)


def try_login_user(s: Session, user_login: LoginRequest) -> UserGet | None:
    """Retrieve user data if login is successful.

    Args:
        s (Session): session to communicate with the database
        user_login (LoginRequest): input user credentials

    Returns:
        UserGet | None: User data if login is successful, otherwise None.
    """

    user_entry = queries.try_get_user_by_username(s, user_login.username)

    if user_entry is not None and check_password(user_login.password, user_entry.hashed_password):
        return db_user_to_user(user_entry)

    return None


def get_user_rank(s: Session, uuid: UUID) -> int:
    """Get global rank of the user.

    Args:
        s (Session): session to communicate with the database
        uuid (UUID): uuid of user to get rank from

    Returns:
        int: rank of the user
    """

    return -1


def get_user_green_score(s: Session, uuid: UUID) -> int:
    """Get green score of the user.

    Args:
        s (Session): session to communicate with the database
        uuid (UUID): uuid of user to get green score for

    Returns:
        int: total green score of the user
    """

    return -1


def get_user_solved(s: Session, uuid: UUID) -> dict[str, int]:
    """Get statistics about the number of solved submissions per difficulty level

    Args:
        s (Session): session to communicate with the database
        uuid (UUID): uuid of user to get number of solved submissions for

    Returns:
        dict[str, int]: number of solved submissions per difficulty level
    """

    easy = queries.get_solved_submissions_by_difficulty(s, uuid, Difficulty.EASY)
    medium = queries.get_solved_submissions_by_difficulty(s, uuid, Difficulty.MEDIUM)
    hard = queries.get_solved_submissions_by_difficulty(s, uuid, Difficulty.HARD)

    total = easy + medium + hard

    return {"total": total, "easy": easy, "medium": medium, "hard": hard}


def get_user_language_stats(s: Session, uuid: UUID) -> list[dict]:
    """Get statistics about the number of solved submissions per language

    Args:
        s (Session): session to communicate with the database
        uuid (UUID): uuid of user to get number of solved submissions for

    Returns:
        list[dict]: every dict contains the language and the number of solved submissions
    """

    return [{"language": "python", "solved": 0}, {"language": "C", "solved": 0}]


def get_recent_submissions(s: Session, uuid: UUID, n: int) -> list[dict]:
    """Get n most recent submissions from user.

    Args:
        s (Session): session to communicate with the database
        uuid (UUID): uuid of user to get recent submissions for
        n (int): number of submissions to retrieve

    Returns:
        list[dict]: list with most recent submissions
    """

    return []
