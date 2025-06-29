"""
Module for all high-level operations that act indirectly on the database
- Functions here do not directly use DB models, unless to pass them around or convert them
- This is only for database actions, or DB model processing. All other actions should happen
  in actions.py
- Should raise HTTPExceptions when something is going wrong
"""

from datetime import datetime
from typing import cast
from uuid import UUID

from fastapi import HTTPException
from loguru import logger
from sqlmodel import Session

from common.auth import check_password, hash_password
from common.languages import Language
from common.schemas import (
    AddProblemRequest,
    LeaderboardRequest,
    LeaderboardResponse,
    LoginRequest,
    PermissionLevel,
    ProblemDetailsResponse,
    ProblemsListResponse,
    RegisterRequest,
    RemoveProblemResponse,
    SubmissionCreate,
    SubmissionFull,
    SubmissionIdentifier,
    SubmissionMetadata,
    SubmissionResult,
    SubmissionRetrieveRequest,
    UserGet,
)
from common.typing import Difficulty
from db.engine import queries
from db.engine.queries import DBCommitError, DBEntryNotFoundError
from db.models.convert import (
    append_submission_results,
    db_problem_to_metadata,
    db_problem_to_problem_get,
    db_submission_to_submission_create_response,
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
    """Create problem in the database and store the wrappers and inputs in storage.

    Args:
        s (Session): session to communicate with the database
        problem (AddProblemRequest): problem to add

    Returns:
        ProblemDetailsResponse: information about problem in the database
    """
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
    """Remove problem from the database

    Args:
        s (Session): session to communicate with the database
        problem_id (int): id of the problem to remove

    Raises:
        DBEntryNotFoundError: if problem is not found

    Returns:
        RemoveProblemResponse: response if removal was successful or not
    """
    problem = queries.try_get_problem(s, problem_id)
    if problem is None:
        raise DBEntryNotFoundError()

    queries.delete_entry(s, problem)
    return RemoveProblemResponse(problem_id=problem_id, deleted=True)


def create_submission(s: Session, submission: SubmissionCreate) -> SubmissionIdentifier:
    """Create submission entry in the database and store code on disk.

    Args:
        s (Session): session to communicate with the database
        submission (SubmissionCreate): submission to create

    Returns:
        SubmissionIdentifier: identifier of submission in the database
    """
    submission_entry = submission_create_to_db_submission(submission)

    storage.store_code(submission)

    _commit_or_500(s, submission_entry)

    return db_submission_to_submission_create_response(submission_entry)


def update_submission(s: Session, submission_result: SubmissionResult) -> SubmissionMetadata:
    """Update submission with the results coming from the execution engine.

    Args:
        s (Session): session to communicate with the database
        submission_result (SubmissionResult): results from the execution engine

    Raises:
        HTTPException: 404 if submission is not found

    Returns:
        SubmissionMetadata: metadata of the submission
    """
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
    """Get leaderboard from the database.

    Args:
        s (Session): session to communicate with the database
        board_request (LeaderboardRequest): leadearboard to get from the database

    Returns:
        LeaderboardResponse: leaderboard from the database
    """
    return queries.get_leaderboard(s, board_request)


def get_submissions(s: Session, offset: int, limit: int) -> list[SubmissionMetadata]:
    """Get submissions from the database.

    Args:
        s (Session): session to communicate with the database
        offset (int): start index
        limit (int): number of indices to retrieve

    Returns:
        list[SubmissionMetadata]: get submissions from database
    """
    return [
        db_submission_to_submission_metadata(entry)
        for entry in queries.get_submissions(s, offset, limit)
    ]


def get_submission_result(s: Session, submission_uuid: UUID, user_uuid: UUID) -> SubmissionResult:
    """Gets submission entry from database and retrieves data from relevant fields.

    Args:
        s (Session): session to communicate to the databse
        submission_uuid (UUID): uuid of the submission to retrieve
        user_uuid (UUID): uuid of the author of the submission

    Returns:
        SubmissionResult: fields changed by the execution engine
    """
    result = queries.get_submission_result(s, user_uuid, submission_uuid)

    return SubmissionResult(
        submission_uuid=result.submission_uuid,
        runtime_ms=result.runtime_ms,
        emissions_kg=result.emissions_kg,
        energy_usage_kwh=result.energy_usage_kwh,
        successful=bool(result.successful),
        error_reason=result.error_reason,
        error_msg=result.error_msg,
    )


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
        raise DBEntryNotFoundError

    problem = cast(ProblemEntry, problem)  # Solves type issues

    problem_get = db_problem_to_problem_get(problem)

    try:
        problem_get.template_code = storage.load_template_code(problem_get)
        problem_get.wrappers = storage.load_wrapper_code(problem_get)
    except FileNotFoundError:
        problem_get.template_code = ""
        problem_get.wrappers = [[""]]

    return problem_get


def read_problems(s: Session, offset: int, limit: int) -> list[ProblemDetailsResponse]:
    """Read problems from the databse

    Args:
        s (Session): session to communicate with the database
        offset (int): starting index
        limit (int): number of problems to retrieve

    Returns:
        list[ProblemDetailsResponse]: problems from the database
    """
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
    """Update user data: avatar
    Args:
        s (Session): session to communicate with the database
        user_uuid (UUID): unique user identifier
        avatar (str): index of user avatar

    Returns:
        UserGet: updated user data
    """

    user_entry = queries.get_user_by_uuid(s, user_uuid)
    queries.update_user_avatar(s, user_entry, int(avatar))

    return db_user_to_user(user_entry)


def update_user_private(s: Session, user_uuid: UUID, private: str) -> UserGet:
    """Update user data: privacy
    Args:
        s (Session): session to communicate with the database
        user_uuid (UUID): unique user identifier
        private (bool): opt-out of leaderboard

    Returns:
        UserGet: updated user data
    """

    user_entry = queries.get_user_by_uuid(s, user_uuid)
    queries.update_user_private(s, user_entry, bool(int(private)))

    return db_user_to_user(user_entry)


def update_user_username(s: Session, user_uuid: UUID, username: str) -> UserGet:
    """Update user data: username
    Args:
        s (Session): session to communicate with the database
        user_uuid (UUID): unique user identifier
        username (str): new username for user

    Returns:
        UserGet: updated user data
    """

    user_entry = queries.get_user_by_uuid(s, user_uuid)
    queries.update_user_username(s, user_entry, username)

    return db_user_to_user(user_entry)


def update_user_pwd(s: Session, user_uuid: UUID, pwd: str) -> UserGet:
    """Update user data: password
    Args:
            s (Session): session to communicate with the database
        user_uuid (UUID): unique user identifier
        pwd (str): new pwd for user

    Returns:
        UserGet: updated user data
    """

    user_entry = queries.get_user_by_uuid(s, user_uuid)
    hashed_pwd = hash_password(pwd)
    queries.update_user_pwd(s, user_entry, hashed_pwd)

    return db_user_to_user(user_entry)


def try_get_problem(s: Session, pid: int) -> ProblemEntry | None:
    """Try to get problem from pid.

    Args:
        s (Session): session to communicate with the database
        pid (int): problem id of the problem to get

    Returns:
        ProblemEntry | None: problem data if problem can be found
    """
    return queries.try_get_problem(s, pid)


def try_get_user_by_uuid(s: Session, uuid: UUID) -> UserEntry | None:
    """Try to get user from uuid.

    Args:
        s (Session): session to communicate with the database
        uuid (UUID): uuid of the user

    Returns:
        UserEntry | None: user data if user can be found
    """
    return queries.try_get_user_by_uuid(s, uuid)


def get_user_by_uuid(s: Session, uuid: UUID) -> UserEntry:
    """Get user from uuid.

    Args:
        s (Session): session to communicate with the database
        uuid (UUID): uuid of the user

    Raises:
        DBEntryNotFound: if no user exists with the uuid

    Returns:
        UserEntry: user data
    """
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


def change_user_permission(s: Session, username: str, permission: PermissionLevel) -> UserGet:
    """
    Change the permission level of a user.
    :param username: The username of the user to change
    :param permission: The new permission level to set
    :returns: Updated UserGet object
    """
    user_entry = queries.get_user_by_username(s, username)

    if not user_entry:
        raise HTTPException(status_code=404, detail="ERROR_USERNAME_NOT_FOUND")

    user_entry.permission_level = permission
    _commit_or_500(s, user_entry)

    return db_user_to_user(user_entry)


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

    language_stats = []

    for language in Language:
        language_stats.append(
            {
                "language": language.value,
                "solved": queries.get_solved_submissions_by_language(s, uuid, language),
            }
        )

    return language_stats


def get_recent_submissions(s: Session, uuid: UUID, n: int) -> list[dict]:
    """Get n most recent submissions from user.

    Args:
        s (Session): session to communicate with the database
        uuid (UUID): uuid of user to get recent submissions for
        n (int): number of submissions to retrieve

    Returns:
        list[dict]: list with most recent submissions
    """

    recents = queries.get_recent_submissions(s, uuid, n)
    output = []

    for submission in recents:
        output.append(
            {
                "id": submission[0],
                "submission_id": submission[1],
                "title": submission[2],
                "created_at": datetime.fromtimestamp(submission[3]).isoformat(),
            }
        )

    return output
