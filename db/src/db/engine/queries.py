"""
Module for all low-level operations that act directly on the database engine
- Functions here only touch DB models (no Pydantic inter-service communication models)
- Shouldn't raise HTTPExceptions, but rather specific exceptions that are caught upstream
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy import func
from sqlmodel import Session, select

from common.schemas import LeaderboardEntryGet, LeaderboardResponse
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


def get_leaderboard(s: Session) -> LeaderboardGet:
    """
    Reads the leaderboard for the users with the best scores
    """

    # TODO: This needs rewriting, several things seem wrong, and the for-loop should be
    #       handled in the query by the database. I think this is over-engineered

    query = (
        select(
            UserEntry.username,
            func.sum(SubmissionEntry.runtime_ms).label("total_score"),
            func.count(  # pylint: disable=not-callable
                func.distinct(SubmissionEntry.problem_id)
            ).label("problems_solved"),
        )
        .select_from(SubmissionEntry)
        .join(UserEntry)
        .where(SubmissionEntry.successful is True)
        .group_by(SubmissionEntry.uuid, UserEntry.username)  # type:ignore
        .order_by(func.sum(SubmissionEntry.runtime_ms).desc())
    )

    results = s.exec(query).all()

    return LeaderboardGet(
        entries=[
            LeaderboardEntryGet(
                username=username, total_score=total_score or 0, problems_solved=problems_solved
            )
            for username, total_score, problems_solved in results
        ]
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
