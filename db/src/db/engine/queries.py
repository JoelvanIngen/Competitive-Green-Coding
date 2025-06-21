"""
Module for all low-level operations that act directly on the database engine
- Functions here only touch DB models (no Pydantic inter-service communication models)
- Shouldn't raise HTTPExceptions, but rather specific exceptions that are caught upstream
"""

from typing import Sequence
from uuid import UUID

from sqlmodel import Session, col, func, select

from common.schemas import LeaderboardRequest, LeaderboardResponse, UserScore
from db.models.db_schemas import ProblemEntry, SubmissionEntry, UserEntry
from db.typing import DBEntry


class DBEntryNotFoundError(Exception):
    """Raised when a function with mandatory return value couldn't find entry in database"""


class DBCommitError(Exception):
    """Raised when a commit error occurs"""


def commit_entry(session: Session, entry: DBEntry):
    """
    Commits an entry to the database. Performs a rollback in case of error.
    :raises DBCommitError: If commit fails
    """

    session.add(entry)
    try:
        session.commit()
        session.refresh(entry)
    except Exception as e:
        # Make sure an exception doesn't contaminate the DB
        session.rollback()
        raise DBCommitError() from e


def get_leaderboard(s: Session, board_request: LeaderboardRequest) -> LeaderboardResponse:
    """
    Get the leaderboard for a specific problem.

    Exclude users that want to remain private,
    or haven't submitted a successful solution.
    Shows only the best submission per user.
    """

    #  TODO: score calculator, runtime_ms is placeholder for now

    try:
        query: Select = (
            select(
                UserEntry.uuid,
                UserEntry.username,
                func.min(SubmissionEntry.energy_usage_kwh).label("least_energy_consumed"),
            )
            .select_from(SubmissionEntry)
            .join(
                UserEntry,
                SubmissionEntry.user_uuid == UserEntry.uuid,
            )
            .where(SubmissionEntry.problem_id == board_request.problem_id)
            .where(SubmissionEntry.successful.is_(True))
            .where(UserEntry.private.is_(False))
            .group_by(
                col(UserEntry.uuid),
                col(UserEntry.username),
            )
            .order_by(func.min(SubmissionEntry.energy_usage_kwh).asc())
            .offset(board_request.first_row)
            .limit(board_request.last_row - board_request.first_row)
        )
        results = s.exec(query).all()
    except Exception as e:
        raise DBEntryNotFoundError() from e

    scores = [UserScore(username=result[1], score=result[2]) for result in results]

    problem = try_get_problem(s, board_request.problem_id)
    if problem is None:
        raise DBEntryNotFoundError()

    return LeaderboardResponse(
        problem_id=problem.problem_id,
        problem_name=problem.name,
        problem_language=problem.language,
        problem_difficulty=problem.difficulty,
        scores=scores,
    )


def get_users(s: Session, offset: int, limit: int) -> Sequence[UserEntry]:
    return s.exec(select(UserEntry).offset(offset).limit(limit)).all()


def try_get_problem(s: Session, pid: int) -> ProblemEntry | None:
    """
    Finds a problem by problem id. Does not raise an exception if not found.
    :param s: SQLModel session
    :param pid: problem id of the problem to lookup
    :return: ProblemEntry if problem exists, else None
    """
    return s.exec(select(ProblemEntry).where(ProblemEntry.problem_id == pid)).first()


def get_problems(s: Session, offset: int, limit: int) -> list[ProblemEntry]:
    return list(s.exec(select(ProblemEntry).offset(offset).limit(limit)).all())


def get_submission_by_sub_uuid(s: Session, uuid: UUID) -> SubmissionEntry:
    res = s.exec(select(SubmissionEntry).where(SubmissionEntry.submission_uuid == uuid)).first()
    if not res:
        raise DBEntryNotFoundError()
    return res


def get_submissions(s: Session, offset: int, limit: int) -> Sequence[SubmissionEntry]:
    return s.exec(select(SubmissionEntry).offset(offset).limit(limit)).all()


def try_get_user_by_username(session: Session, username: str) -> UserEntry | None:
    """
    Finds a user by username. Does not raise an exception if not found.
    :param username: Username of the user to lookup
    :param session: SQLModel session
    :return: UserEntry if user exists, else None
    """
    return session.exec(select(UserEntry).where(UserEntry.username == username)).first()


def try_get_user_by_email(session: Session, email: str) -> UserEntry | None:
    """
    Finds a user by email. Does not raise an exception if not found.
    :param email: email of the user to lookup
    :param session: SQLModel session
    :return: UserEntry if user exists, else None
    """
    return session.exec(select(UserEntry).where(UserEntry.email == email)).first()


def try_get_user_by_uuid(session: Session, uuid: UUID) -> UserEntry | None:
    """
    Finds a user by UUID. Does not raise an exception if not found.
    :param uuid: Uuid of the user to lookup
    :param session: SQLModel session
    :return: UserEntry if user exists, else None
    """
    return session.exec(select(UserEntry).where(UserEntry.uuid == uuid)).first()


def get_user_by_username(s: Session, username: str) -> UserEntry:
    """
    Finds a user by username. Errors if not found.
    :param username: Name of the user to lookup
    :param s: SQLModel session
    :return: UserEntry
    :raises DBEntryNotFoundError: If username is not found
    """
    res = try_get_user_by_username(s, username)
    if not res:
        raise DBEntryNotFoundError
    return res


def get_user_by_uuid(s: Session, uuid: UUID) -> UserEntry:
    """
    Finds a user by UUID. Errors if not found.
    :param uuid: Uuid of the user to lookup
    :param s: SQLModel session
    :return: UserEntry
    :raises DBEntryNotFoundError: If uuid is not found
    """
    res = try_get_user_by_uuid(s, uuid)
    if not res:
        raise DBEntryNotFoundError
    return res


def update_user(
    session: Session,
    user_entry: UserEntry,
    private: bool,
) -> UserEntry:
    """
    Updates a user's privacy setting.
    (Can extend later by adding more parameters as needed)

    Args:
        session: SQLModel session
        user_entry: User to update
        private: New privacy value

    Returns:
        Updated UserEntry

    Raises:
        DBCommitError: If commit fails
    """
    user_entry.private = private
    commit_entry(session, user_entry)
    return user_entry
