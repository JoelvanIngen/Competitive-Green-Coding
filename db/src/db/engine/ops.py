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
    ProblemsListResponse,
    RegisterRequest,
    RemoveProblemResponse,
    SubmissionCreate,
    SubmissionFull,
    SubmissionMetadata,
    SubmissionResult,
    SubmissionRetrieveRequest,
    UserGet,
)
from db.engine import queries
from db.engine.queries import DBCommitError, DBEntryNotFoundError
from db.models.convert import (
    append_submission_results,
    db_problem_to_metadata,
    db_problem_to_problem_get,
    db_submission_to_submission_full,
    db_submission_to_submission_metadata,
    db_user_to_user,
    problem_post_to_db_problem,
    submission_create_to_db_submission,
)
from db.models.db_schemas import ProblemEntry, ProblemTagEntry, UserEntry
from db.storage import storage
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
    problem_get.template_code = problem.template_code
    problem_get.wrappers = problem.wrappers
    storage.store_template_code(problem_get)
    storage.store_wrapper_code(problem_get)

    return problem_get


def remove_problem(s: Session, problem_id: int) -> RemoveProblemResponse:
    problem = queries.try_get_problem(s, problem_id)
    if problem is None:
        raise DBEntryNotFoundError()

    try:
        queries.delete_problem(s, problem)
    except Exception as exc:
        import sys
        print(">>> FULL DELETE FAILURE:", repr(exc), file=sys.stderr, flush=True)
        raise

    return RemoveProblemResponse(problem_id=problem_id, deleted=True)


def create_submission(s: Session, submission: SubmissionCreate) -> SubmissionMetadata:
    submission_entry = submission_create_to_db_submission(submission)

    storage.store_code(submission)

    _commit_or_500(s, submission_entry)

    return db_submission_to_submission_metadata(submission_entry)


def update_submission(s: Session, submission_result: SubmissionResult) -> SubmissionMetadata:
    try:
        submission_entry = queries.get_submission_by_sub_uuid(s, submission_result.submission_uuid)
    except DBEntryNotFoundError as e:
        raise HTTPException(status_code=404, detail="Submission entry not found") from e

    append_submission_results(submission_entry, submission_result)
    _commit_or_500(s, submission_entry)

    return db_submission_to_submission_metadata(submission_entry)


def get_submission_from_retrieve_request(
    s: Session, request: SubmissionRetrieveRequest
) -> SubmissionFull:
    """Get all data related to submission from the retrieve request.

    Args:
        s (Session): session to connect to the databse
        request (SubmissionRetrieveRequest): contains all relevant information to retrieve
            submission

    Returns:
        SubmissionFull: all data related to submission in the retrieve request.
    """

    submission_full = db_submission_to_submission_full(
        queries.get_submission_from_problem_user_ids(s, request.problem_id, request.user_uuid)
    )

    submission_full.code = storage.load_last_submission_code(request)

    return submission_full


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
    problem_get.template_code = storage.load_template_code(problem_get)
    problem_get.wrappers = storage.load_wrapper_code(problem_get)

    return problem_get


def read_problems(s: Session, offset: int, limit: int) -> list[ProblemDetailsResponse]:
    problem_entries = queries.get_problems(s, offset, limit)

    problem_gets = []
    for problem in problem_entries:
        problem_get = db_problem_to_problem_get(problem)
        problem_get.template_code = storage.load_template_code(problem_get)
        problem_get.wrappers = storage.load_wrapper_code(problem_get)
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


def update_user_avatar(s: Session, user_uuid: UUID, avatar: str) -> UserGet:
    """Update user data
    Args:
            s (Session): session to communicate with the database
            user_uuid (UUID): unique user identifier
            avatar (str): index of user avatar

    Returns:
            UserEntry
    """

    user_entry = queries.get_user_by_uuid(s, user_uuid)
    queries.update_user_avatar(s, user_entry, int(avatar))

    return db_user_to_user(user_entry)


def update_user_private(s: Session, user_uuid: UUID, private: str) -> UserGet:
    """Update user data
    Args:
            s (Session): session to communicate with the database
            user_uuid (UUID): unique user identifier
            private (bool): opt-out of leaderboard

    Returns:
            UserEntry
    """

    user_entry = queries.get_user_by_uuid(s, user_uuid)
    queries.update_user_private(s, user_entry, bool(int(private)))

    return db_user_to_user(user_entry)


def update_user_username(s: Session, user_uuid: UUID, username: str) -> UserGet:
    """Update user data
    Args:
            s (Session): session to communicate with the database
            user_uuid (UUID): unique user identifier
            username (str): new username for user

    Returns:
            UserEntry
    """

    user_entry = queries.get_user_by_uuid(s, user_uuid)
    queries.update_user_username(s, user_entry, username)

    return db_user_to_user(user_entry)


def update_user_pwd(s: Session, user_uuid: UUID, pwd: str) -> UserGet:
    """Update user data
    Args:
            s (Session): session to communicate with the database
            user_uuid (UUID): unique user identifier
            pwd (str): new pwd for user

    Returns:
            UserEntry
    """

    user_entry = queries.get_user_by_uuid(s, user_uuid)
    hashed_pwd = hash_password(pwd)
    queries.update_user_pwd(s, user_entry, hashed_pwd)

    return db_user_to_user(user_entry)


def try_get_problem(s: Session, pid: int) -> ProblemEntry | None:
    return queries.try_get_problem(s, pid)


def try_get_user_by_uuid(s: Session, uuid: UUID) -> UserEntry | None:
    return queries.try_get_user_by_uuid(s, uuid)


def get_user_by_uuid(s: Session, uuid: UUID) -> UserEntry:
    return queries.get_user_by_uuid(s, uuid)


def get_problem_metadata(s: Session, offset: int, limit: int) -> ProblemsListResponse:
    """
    Retrieves a list of problem metadata from the database.
    :param s: SQLAlchemy session
    :param offset: Offset for pagination
    :param limit: Limit for pagination
    :returns: ProblemsListResponse containing total count and list of problem metadata
    """
    problems = queries.get_problems(s, offset, limit)
    metadata = [db_problem_to_metadata(p) for p in problems]
    return ProblemsListResponse(total=len(problems), problems=metadata)
