"""
Module for all high-level operations that act indirectly on the database
- Functions here do not directly use DB models, unless to pass them around or convert them
- This is only for database actions, or DB model processing. All other actions should happen
  in actions.py
- Should raise HTTPExceptions when something is going wrong
"""

from typing import cast

from fastapi import HTTPException
from loguru import logger
from sqlmodel import Session

from db.auth import check_email, check_password, check_username, hash_password
from db.engine import queries
from db.engine.queries import DBCommitError
from db.models.convert import (
    db_problem_to_problem_get,
    db_submission_to_submission_get,
    db_user_to_user,
    problem_post_to_db_problem,
    submission_post_to_db_submission,
)
from db.models.db_schemas import ProblemEntry, ProblemTagEntry, UserEntry
from db.models.schemas import (
    LeaderboardGet,
    ProblemGet,
    ProblemPost,
    SubmissionGet,
    SubmissionPost,
    UserGet,
    UserLogin,
    UserRegister,
)
from db.typing import DBEntry


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


def create_problem(s: Session, problem: ProblemPost) -> ProblemGet:
    problem_entry = problem_post_to_db_problem(problem)

    _commit_or_500(s, problem_entry)

    problem_id = problem_entry.problem_id
    for tag in problem.tags:
        problem_tag_entry = ProblemTagEntry(problem_id=problem_id, tag=tag)
        _commit_or_500(s, problem_tag_entry)

    problem_get = db_problem_to_problem_get(problem_entry)

    return problem_get


def create_submission(s: Session, submission: SubmissionPost) -> SubmissionGet:
    submission_entry = submission_post_to_db_submission(submission)

    # TODO: Code saving in storage
    # code_handler(submission.code)

    _commit_or_500(s, submission_entry)

    return db_submission_to_submission_get(submission_entry)


def get_leaderboard(s: Session) -> LeaderboardGet:
    return queries.get_leaderboard(s)


def get_submissions(s: Session, offset: int, limit: int) -> list[SubmissionGet]:
    return [
        db_submission_to_submission_get(entry)
        for entry in queries.get_submissions(s, offset, limit)
    ]


def get_user_from_username(s: Session, username: str) -> UserGet:
    """
    :raises DBEntryNotFoundError: If username is not found (from downstream)
    """
    return db_user_to_user(queries.get_user_by_username(s, username))


def read_problem(s: Session, problem_id: int) -> ProblemGet:
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


def read_problems(s: Session, offset: int, limit: int) -> list[ProblemGet]:
    problem_entries = queries.get_problems(s, offset, limit)

    problem_gets = []
    for problem in problem_entries:
        problem_get = db_problem_to_problem_get(problem)
        problem_gets.append(problem_get)

    return problem_gets


def register_new_user(s: Session, user: UserRegister) -> UserGet:
    """
    Register a new user to the DB
    :returns: The created DB user entry
    :raises HTTPException 400: On bad username
    :raises HTTPException 409: On existing username
    :raises HTTPException 500: On DB error
    """

    if queries.try_get_user_by_username(s, user.username) is not None:
        raise HTTPException(status_code=409, detail="PROB_USERNAME_EXISTS")

    if queries.try_get_user_by_email(s, user.email) is not None:
        raise HTTPException(status_code=409, detail="PROB_EMAIL_REGISTERED")

    if check_email(user.email) is False:
        raise HTTPException(status_code=422, detail="PROB_INVALID_EMAIL")

    if check_username(user.username) is False:
        raise HTTPException(status_code=422, detail="PROB_USERNAME_CONSTRAINTS")

    # TODO: Password constraints

    # TODO: Make all users lowest permission, and allow admins to elevate permissions of
    #       existing users later (would be attack vector otherwise)
    user_entry = UserEntry(
        username=user.username,
        email=user.email,
        permission_level=user.permission_level,
        hashed_password=hash_password(user.password),
    )

    _commit_or_500(s, user_entry)

    return db_user_to_user(user_entry)


def login_user(s: Session, user_login: UserLogin) -> UserGet:
    """Retrieve user data if login is successful.

    Args:
        s (Session): session to communicate with the database
        user_login (UserLogin): input user credentials

    Raises:
        HTTPException: 422 PROB_USERNAME_CONSTRAINTS if username does not match constraints
        HTTPException: 401 Unauthorized if username and password do not match

    Returns:
        UserGet: JSON Web Token of user
    """

    if check_username(user_login.username) is False:
        raise HTTPException(status_code=422, detail="PROB_USERNAME_CONSTRAINTS")

    user_entry = queries.try_get_user_by_username(s, user_login.username)

    if user_entry is not None and check_password(user_login.password, user_entry.hashed_password):
        return db_user_to_user(user_entry)
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
