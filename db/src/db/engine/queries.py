"""
Module for all low-level operations that act directly on the database engine
- Functions here only touch DB models (no Pydantic inter-service communication models)
- Shouldn't raise HTTPExceptions, but rather specific exceptions that are caught upstream
"""

from typing import Sequence
from uuid import UUID

from sqlmodel import Session, desc, distinct, func, select

from common.languages import Language
from common.schemas import LeaderboardRequest, LeaderboardResponse, UserScore
from common.typing import Difficulty
from db.models.db_schemas import ProblemEntry, SubmissionEntry, UserEntry
from db.typing import DBEntry


class DBEntryNotFoundError(Exception):
    """Raised when a function with mandatory return value couldn't find entry in database"""


class DBCommitError(Exception):
    """Raised when a commit error occurs"""


class SubmissionNotReadyError(Exception):
    """Raised when a submission exists but has not yet finished executing"""


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


def delete_entry(session: Session, entry: DBEntry) -> None:
    try:
        session.delete(entry)
        session.commit()
    except Exception as exc:
        session.rollback()
        raise DBCommitError from exc


def get_leaderboard(s: Session, board_request: LeaderboardRequest) -> LeaderboardResponse:
    """
    Get the leaderboard for a specific problem.

    Exclude users that want to remain private,
    or haven't submitted a successful solution.
    Shows only the best submission per user.
    """
    try:
        query = (
            select(
                UserEntry.uuid,
                UserEntry.username,
                UserEntry.avatar_id,
                func.min(SubmissionEntry.energy_usage_kwh).label("least_energy_consumed"),
            )
            .select_from(SubmissionEntry)
            .join(
                UserEntry,
                SubmissionEntry.user_uuid == UserEntry.uuid,  # type: ignore[arg-type]
            )
            .where(SubmissionEntry.problem_id == board_request.problem_id)
            .where(SubmissionEntry.successful == True)  # type: ignore[arg-type] # pylint: disable=singleton-comparison  # noqa: E712, E501
            .where(UserEntry.private == False)  # type: ignore[arg-type]  # pylint: disable=singleton-comparison  # noqa: E712, E501
            .group_by(UserEntry.uuid, UserEntry.username)  # type: ignore[arg-type]
            .order_by(func.min(SubmissionEntry.energy_usage_kwh).asc())
            .offset(board_request.first_row)
            .limit(board_request.last_row - board_request.first_row)
        )
        results = s.exec(query).all()
    except Exception as exc:
        raise DBEntryNotFoundError from exc

    scores = [
        UserScore(username=username, avatar_id=avatar_id, score=energy)
        for (_, username, avatar_id, energy) in results
    ]

    problem = try_get_problem(s, board_request.problem_id)
    if problem is None:
        raise DBEntryNotFoundError

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


def get_submission_from_problem_user_ids(
    s: Session, problem_id: int, user_uuid: UUID
) -> SubmissionEntry:
    """Get most recent submission entry that a user with user_uuid made for the problem with
    problem_id.

    Args:
        s (Session): session to communicate with the database
        problem_id (int): problem id of the problem
        user_uuid (UUID): user uuid of the submission author

    Raises:
        DBEntryNotFoundError: if no submission is found for this user for this problem

    Returns:
        SubmissionEntry: data of problem stored in the database
    """

    result = s.exec(
        select(SubmissionEntry)
        .where(SubmissionEntry.problem_id == problem_id)
        .where(SubmissionEntry.user_uuid == user_uuid)
        .order_by(desc(SubmissionEntry.timestamp))
    ).first()
    if not result:
        raise DBEntryNotFoundError()
    return result


def get_submissions(s: Session, offset: int, limit: int) -> Sequence[SubmissionEntry]:
    return s.exec(select(SubmissionEntry).offset(offset).limit(limit)).all()


def get_submission_result(s: Session, user_uuid: UUID, submission_uuid: UUID) -> SubmissionEntry:
    """Fetch the submission for this user and submission UUID combination and ensure it's been
    executed.

    Args:
        s (Session): session to connect to the database
        user_uuid (UUID): uuid of the user which made the submission
        submission_uuid (UUID): submission uuid of the latest submission

    Raises:
        DBEntryNotFoundError: if no submission is found with this submission uuid and user uuid
        SubmissionNotReadyError: if the submission has not been executed

    Returns:
        SubmissionEntry: database entry of the submission
    """

    result = s.exec(
        select(SubmissionEntry)
        .where(SubmissionEntry.user_uuid == user_uuid)
        .where(SubmissionEntry.submission_uuid == submission_uuid)
    ).first()

    if not result:
        raise DBEntryNotFoundError()

    if not result.executed:
        raise SubmissionNotReadyError()

    return result


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


def update_user_avatar(s: Session, user_entry: UserEntry, avatar: int) -> UserEntry:
    """
    Updates a user's avatar.

    Args:
        session: SQLModel session
        user_entry: User to update
        avatar: New avatar index

    Returns:
        Updated UserEntry

    Raises:
        DBCommitError: If commit fails
    """
    user_entry.avatar_id = avatar
    commit_entry(s, user_entry)

    return user_entry


def update_user_private(s: Session, user_entry: UserEntry, private: bool) -> UserEntry:
    """
    Updates a user's privacy setting.

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
    commit_entry(s, user_entry)

    return user_entry


def update_user_username(s: Session, user_entry: UserEntry, username: str) -> UserEntry:
    """
    Updates a user's name.

    Args:
        session: SQLModel session
        user_entry: User to update
        username: New username string

    Returns:
        Updated UserEntry

    Raises:
        DBCommitError: If commit fails
    """
    user_entry.username = username
    commit_entry(s, user_entry)

    return user_entry


def update_user_pwd(s: Session, user_entry: UserEntry, hashed_pwd: bytes) -> UserEntry:
    """
    Updates a user's name.

    Args:
        session: SQLModel session
        user_entry: User to update
        username: New username string

    Returns:
        Updated UserEntry

    Raises:
        DBCommitError: If commit fails
    """
    user_entry.hashed_password = hashed_pwd
    commit_entry(s, user_entry)

    return user_entry


def get_solved_submissions_by_difficulty(s: Session, uuid: UUID, difficulty: Difficulty) -> int:
    """Retrieve number of solved problems by a user with difficulty 'difficulty'.

    Args:
        s (Session): session to communicate with the database
        uuid (UUID): uuid of user to get number of solved submissions for
        difficulty (Difficulty): difficulty of the submissions

    Returns:
        int: number of sovled problems with difficulty 'difficulty'
    """
    query = (
        select(func.count(distinct(ProblemEntry.problem_id)))
        .join(SubmissionEntry)
        .join(UserEntry)
        .where(SubmissionEntry.user_uuid == uuid)
        .where(SubmissionEntry.successful == True)  # type: ignore[arg-type] # pylint: disable=singleton-comparison  # noqa: E712, E501
        .where(ProblemEntry.difficulty == difficulty)
    )

    result = s.exec(query).first()

    if result:
        return int(result)
    else:
        return 0


def get_solved_submissions_by_language(s: Session, uuid: UUID, language: Language) -> int:
    """Retrieve number of solved problems by a user with language 'language'.

    Args:
        s (Session): session to communicate with the database
        uuid (UUID): uuid of user to get number of solved submissions for
        language (Language): language of the submissions

    Returns:
        int: number of sovled problems with language 'language'
    """
    query = (
        select(func.count(distinct(ProblemEntry.problem_id)))
        .join(SubmissionEntry)
        .where(SubmissionEntry.user_uuid == uuid)
        .where(SubmissionEntry.successful == True)  # type: ignore[arg-type] # pylint: disable=singleton-comparison  # noqa: E712, E501
        .where(SubmissionEntry.language == language)
    )

    result = s.exec(query).first()

    if result:
        return int(result)
    else:
        return 0


def get_recent_submissions(
    s: Session, user_uuid: UUID, n: int
) -> list:
    """Get most recent submission entry that a user with user_uuid made for the problem with
    problem_id.

    Args:
        s (Session): session to communicate with the database
        problem_id (int): problem id of the problem
        user_uuid (UUID): user uuid of the submission author

    Raises:
        DBEntryNotFoundError: if no submission is found for this user for this problem

    Returns:
        list: data of problem stored in the database
    """

    result = s.exec(
        select(
            SubmissionEntry.problem_id,
            SubmissionEntry.submission_uuid,
            ProblemEntry.name,
            SubmissionEntry.timestamp
        )
        .join(ProblemEntry)
        .where(SubmissionEntry.user_uuid == user_uuid)
        .order_by(desc(SubmissionEntry.timestamp))
        .limit(n)
    ).all()

    return result
