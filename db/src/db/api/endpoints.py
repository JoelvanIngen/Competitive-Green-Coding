import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, SQLModel, create_engine, func, select

from db.api.modules.bitmap_translator import translate_bitmap_to_tags, translate_tags_to_bitmap
from db.api.modules.hasher import check_password, hash_password
from db.api.modules.jwt_handler import create_access_token, decode_access_token
from db.models.db_schemas import ProblemEntry, SubmissionEntry, UserEntry
from db.models.schemas import (
    LeaderboardEntryGet,
    LeaderboardGet,
    ProblemGet,
    ProblemPost,
    SubmissionPost,
    TokenResponse,
    UserGet,
    UserLogin,
    UserRegister,
)

SQLITE_FILE_NAME = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

connect_args = {"check_same_thread": False}
engine = create_engine(SQLITE_URL, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


router = APIRouter()


def try_get_user_by_username(username: str, session: SessionDep) -> UserEntry | None:
    return session.exec(select(UserEntry).where(UserEntry.username == username)).first()


def try_get_user_by_uuid(_uuid: uuid.UUID, session: SessionDep) -> UserEntry | None:
    return session.exec(select(UserEntry).where(UserEntry.uuid == _uuid)).first()


def get_user_by_username(username: str, session: SessionDep) -> UserEntry:
    res = try_get_user_by_username(username, session)
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    return res


def get_user_by_uuid(_uuid: uuid.UUID, session: SessionDep) -> UserEntry:
    res = try_get_user_by_uuid(_uuid, session)
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    return res


def code_handler(code: str) -> None:
    raise NotImplementedError(code)  # Use variable code so pylint doesn't warn


def add_commit_refresh(entry: UserEntry | ProblemEntry | SubmissionEntry, session: SessionDep):
    session.add(entry)
    session.commit()
    session.refresh(entry)


@router.post("/auth/register/")
async def register_user(user: UserRegister, session: SessionDep) -> UserGet:
    if get_user_by_username(user.username, session) is not None:
        raise HTTPException(status_code=403, detail="Username already in use")

    user_entry = UserEntry(
        username=user.username, email=user.email, permission_level=user.permission_level
    )
    user_entry.uuid = uuid.uuid4()
    user_entry.hashed_password = hash_password(user.password)

    add_commit_refresh(user_entry, session)

    user_get = UserGet(uuid=user_entry.uuid, username=user.username, email=user.email)

    return user_get


@router.post("/auth/login/")
async def login_user(login: UserLogin, session: SessionDep) -> TokenResponse:
    user_entry = get_user_by_username(login.username, session)

    if not (user_entry and check_password(login.password, user_entry.hashed_password)):
        raise HTTPException(status_code=409, detail="User authentication failure")

    data = {
        "uuid": str(user_entry.uuid),
        "username": user_entry.username,
        "email": user_entry.email,
        "permission_level": user_entry.permission_level,
    }
    jwt_token = create_access_token(data)
    return TokenResponse(access_token=jwt_token)


@router.post("/users/me/")
async def get_active_user(token: TokenResponse, session: SessionDep) -> UserGet:
    try:
        data = decode_access_token(token.access_token)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e

    user_uuid = uuid.UUID(data["uuid"])
    user_entry = get_user_by_uuid(user_uuid, session)
    user_get = UserGet(
        uuid=user_uuid,
        username=user_entry.username,
        email=user_entry.email,
        permission_level=user_entry.permission_level,
    )

    return user_get


# WARNING: for development purposes only
@router.get("/users/")
async def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=1000)] = 1000,
) -> list[UserEntry]:
    users = session.exec(select(UserEntry).offset(offset).limit(limit)).all()
    return list(users)


@router.get("/users/{username}")
async def read_user(username: str, session: SessionDep) -> UserGet:
    user = get_user_by_username(username, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_get = UserGet(uuid=user.uuid, username=user.username, email=user.email)

    return user_get


@router.get("/leaderboard")
async def get_leaderboard(session: SessionDep) -> LeaderboardGet:
    query = (
        select(
            UserEntry.username,
            func.sum(SubmissionEntry.score).label("total_score"),
            func.count(  # pylint: disable=not-callable
                func.distinct(SubmissionEntry.problem_id)
            ).label("problems_solved"),
        )
        .select_from(SubmissionEntry)
        .join(UserEntry)
        .where(SubmissionEntry.successful is True)
        .group_by(SubmissionEntry.uuid, UserEntry.username)  # type:ignore
        .order_by(func.sum(SubmissionEntry.score).desc())
    )

    results = session.exec(query).all()

    leaderboard = LeaderboardGet(
        entries=[
            LeaderboardEntryGet(
                username=username, total_score=total_score or 0, problems_solved=problems_solved
            )
            for username, total_score, problems_solved in results
        ]
    )

    return leaderboard


@router.post("/problems/")
async def create_problem(problem: ProblemPost, session: SessionDep) -> ProblemEntry:
    problem_entry = ProblemEntry(name=problem.name, description=problem.description)
    problem_entry.tags = translate_tags_to_bitmap(problem.tags)

    add_commit_refresh(problem_entry, session)

    return problem_entry


@router.get("/problems/")
async def read_problems(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[ProblemGet]:
    problems = session.exec(select(ProblemEntry).offset(offset).limit(limit)).all()

    problem_gets = []
    for problem in problems:
        problem_get = ProblemGet(
            problem_id=problem.problem_id,
            name=problem.name,
            description=problem.description,
            tags=[],
        )
        problem_get.tags = translate_bitmap_to_tags(problem.tags)
        problem_gets.append(problem_get)

    return problem_gets


@router.get("/problems/{problem_id}")
async def read_problem(problem_id: int, session: SessionDep) -> ProblemGet:
    problem = session.get(ProblemEntry, problem_id)
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


@router.post("/submissions/")
async def create_submission(submission: SubmissionPost, session: SessionDep) -> SubmissionEntry:
    submission_entry = SubmissionEntry(
        problem_id=submission.problem_id,
        uuid=submission.uuid,
        runtime_ms=submission.runtime_ms,
        timestamp=submission.timestamp,
        successful=submission.successful,
        code=submission.code,
    )

    # Get the maximum sid across all submissions
    max_sid = session.exec(
        select(func.max(SubmissionEntry.sid))
        .where(SubmissionEntry.problem_id == submission.problem_id)
        .where(SubmissionEntry.uuid == submission.uuid)
    ).first()

    code_handler(submission.code)

    if max_sid is not None:
        submission_entry.sid = max_sid + 1
    else:
        submission_entry.sid = 0

    add_commit_refresh(submission_entry, session)

    return submission_entry


@router.get("/submissions/")
async def read_submission(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
) -> list[SubmissionEntry]:
    submissions = session.exec(select(SubmissionEntry).offset(offset).limit(limit)).all()
    return list(submissions)


@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "message": "DB service is running"}
