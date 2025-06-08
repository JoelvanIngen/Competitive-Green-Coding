"""
Module for all high-level operations that act indirectly on the database
- Functions here do not directly use DB models, unless to pass them around or convert them
- Should raise HTTPExceptions when something is going wrong
"""

from fastapi import HTTPException
from loguru import logger
from sqlmodel import Session

from db.api.modules.bitmap_translator import translate_tags_to_bitmap, translate_bitmap_to_tags
from db.api.modules.hasher import hash_password
from db.engine.queries import try_get_user_by_username, commit_entry, DBCommitError
from db.models.convert import submission_post_to_db_submission
from db.models.db_schemas import UserEntry, DBEntry, ProblemEntry, SubmissionEntry
from db.models.schemas import UserRegister, UserLogin, TokenResponse, ProblemPost, ProblemGet, SubmissionPost


def _commit_or_500(session, entry: DBEntry):
    """
    Attempts to commit the given entry to the database
    :raises HTTPException 500: On DB error
    """

    try:
        commit_entry(session, entry)
    except DBCommitError as e:
        logger.error(f"DB commit error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


def create_submission(s: Session, submission: SubmissionPost):
    submission_entry = submission_post_to_db_submission(submission)

    # TODO: Code saving in storage
    # code_handler(submission.code)

    _commit_or_500(s, submission_entry)

    return submission_entry


def create_problem(s: Session, problem: ProblemPost) -> None:
    problem_entry = ProblemEntry(name=problem.name, description=problem.description)
    problem_entry.tags = translate_tags_to_bitmap(problem.tags)

    _commit_or_500(s, problem_entry)


def read_problem(s: Session, problem_id: int) -> ProblemGet:
    """
    Attempts to read the given problem from the database
    :raises HTTPException 404: Problem not found if problem not in DB
    """

    problem = s.get(ProblemEntry, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    problem_get = ProblemGet(
        problem_id=problem.problem_id,
        name=problem.name,
        description=problem.description,
        tags=[],
    )

    problem_get.tags = translate_bitmap_to_tags(problem.tags)

    return problem_get


def register_new_user(s: Session, user: UserRegister) -> UserEntry:
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

    # Check if user already exists
    if try_get_user_by_username(s, user.username) is not None:
        # 409 conflict
        raise HTTPException(status_code=409, detail="Username already in use")

    # TODO: Make all users lowest permission, and allow admins to elevate permissions of
    #       existing users later (would be attack vector otherwise)
    user_entry = UserEntry(
        username=user.username,
        email=user.email,
        permission_level=user.permission_level,
        hashed_password=hash_password(user.password),
    )

    _commit_or_500(s, user_entry)

    return user_entry
