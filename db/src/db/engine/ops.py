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

from db.api.modules.bitmap_translator import translate_bitmap_to_tags, translate_tags_to_bitmap
from db.auth import check_email, hash_password
from db.engine import queries
from db.engine.queries import DBCommitError
from db.models.convert import (
    db_problem_to_problem_get,
    db_submission_to_submission_get,
    db_user_to_user,
    submission_post_to_db_submission,
)
from db.models.db_schemas import ProblemEntry, UserEntry
from db.models.schemas import (
    LeaderboardGet,
    ProblemGet,
    ProblemPost,
    SubmissionGet,
    SubmissionPost,
    UserGet,
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
    problem_entry = ProblemEntry(name=problem.name, description=problem.description)
    problem_entry.tags = translate_tags_to_bitmap(problem.tags)

    _commit_or_500(s, problem_entry)

    problem_get = db_problem_to_problem_get(problem_entry)
    problem_get.tags = translate_bitmap_to_tags(problem_entry.tags)

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

    problem_get.tags = translate_bitmap_to_tags(problem.tags)

    return problem_get


def read_problems(s: Session, offset: int, limit: int) -> list[ProblemGet]:
    problem_entries = queries.get_problems(s, offset, limit)

    problem_gets = []
    for problem in problem_entries:
        problem_get = db_problem_to_problem_get(problem)
        problem_get.tags = translate_bitmap_to_tags(problem.tags)
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

    # TODO: Check validity of username
    # try:
    # check_username_valid
    # If not, raise 400 bad request

    if queries.try_get_user_by_username(s, user.username) is not None:
        raise HTTPException(status_code=409, detail="PROB_USERNAME_EXISTS")

    if queries.try_get_user_by_email(s, user.email) is not None:
        raise HTTPException(status_code=409, detail="PROB_EMAIL_REGISTERED")

    if check_email(user.email) is False:
        raise HTTPException(status_code=422, detail="PROB_INVALID_EMAIL")

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
