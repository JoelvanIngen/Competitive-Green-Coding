from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, SQLModel, create_engine, select, func
import uuid

from models.db_schemas import UserEntry, ProblemEntry, SubmissionEntry
from models.schemas import ProblemGet, ProblemPost, SubmissionPost, LeaderboardEntryGet, \
    LeaderboardGet
from models.schemas import UserRegister, UserGet, UserLogin, TokenResponse

from api.modules.hasher import hash_password, check_password
from api.modules.jwt_creator import create_access_token
from api.modules.bitmap_translator import translate_tags_to_bitmap, translate_bitmap_to_tags


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


router = APIRouter()


def get_user_by_username(username: str, session: SessionDep) -> UserEntry:
    return session.exec(select(UserEntry)
                        .where(UserEntry.username == username)).first()


def add_commit_refresh(entry: UserEntry | ProblemEntry | SubmissionEntry, session: SessionDep):
    session.add(entry)
    session.commit()
    session.refresh(entry)


@router.post("/auth/register/")
async def register_user(user: UserRegister, session: SessionDep) -> UserGet:
    if get_user_by_username(user.username, session) is not None:
        raise HTTPException(status_code=403, detail="Username already in use")

    user_entry = UserEntry(username=user.username, email=user.email)
    user_entry.uuid = uuid.uuid4()
    user_entry.hashed_password = hash_password(user.password)

    add_commit_refresh(user_entry, session)

    user_get = UserGet(uuid=user_entry.uuid, username=user.username, email=user.email)

    return user_get


@router.post("/auth/login/")
async def login_user(login: UserLogin, session: SessionDep) -> TokenResponse:
    user_entry = get_user_by_username(login.username, session)

    if user_entry and check_password(login.password, user_entry.hashed_password):
        data = {
            "uuid": str(user_entry.uuid),
            "username": user_entry.username,
            "email": user_entry.email
        }
        jwt_token = create_access_token(data)
        return TokenResponse(access_token=jwt_token)
    else:
        raise HTTPException(status_code=409, detail="User authentication failure")


# WARNING: for development purposes only
@router.get("/users/")
async def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[UserEntry]:
    users = session.exec(select(UserEntry).offset(offset).limit(limit)).all()
    return users


@router.get("/users/{username}")
async def read_user(username: str, session: SessionDep) -> UserGet:
    user = session.exec(select(UserEntry).where(UserEntry.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_get = UserGet(uuid=user.uuid, username=user.username, email=user.email)

    return user_get


@router.get("/users/leaderboard")
async def get_leaderboard(session: SessionDep, offset: int = 0) -> LeaderboardGet:

    query = (
        select(
            UserEntry.username,
            func.sum(SubmissionEntry.score).label("total_score"),
            func.count(func.distinct(SubmissionEntry.problem_id)).label("problems_solved")
        )
        .select_from(SubmissionEntry)
        .join(UserEntry, SubmissionEntry.uuid == UserEntry.uuid)
        .where(SubmissionEntry.successful is True)
        .group_by(SubmissionEntry.uuid, UserEntry.username)
        .order_by(func.sum(SubmissionEntry.score).desc())
    )

    results = session.exec(query).all()

    leaderboard = LeaderboardGet(entries=[
        LeaderboardEntryGet(
            username=username,
            total_score=total_score or 0,
            problems_solved=problems_solved
        )
        for username, total_score, problems_solved in results
    ])

    return leaderboard


@router.post("/problems/")
async def create_problem(problem: ProblemPost, session: SessionDep) -> ProblemEntry:
    problem_entry = ProblemEntry(name=problem.name, description=problem.description)
    problem_entry.tags = translate_tags_to_bitmap(problem.tags)

    max_problem_id = session.exec(func.max(ProblemEntry.problem_id)).scalar()

    if max_problem_id is not None:
        problem_entry.problem_id = max_problem_id + 1
    else:
        problem_entry.problem_id = 0

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
        problem_get = ProblemGet(problem_id=problem.problem_id, name=problem.name,
                                 description=problem.description,
                                 tags=[])
        problem_get.tags = translate_bitmap_to_tags(problem.tags)
        problem_gets.append(problem_get)

    return problem_gets


@router.get("/problems/{problem_id}")
async def read_problem(problem_id: int, session: SessionDep) -> ProblemGet:
    problem = session.get(ProblemEntry, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    problem_get = ProblemGet(problem_id=problem.problem_id, name=problem.name,
                             description=problem.description,
                             tags=[])

    problem_get.tags = translate_bitmap_to_tags(problem.tags)

    return problem_get


def code_handler(code: str):
    ...


@router.post("/submissions/")
async def create_submission(submission: SubmissionPost, session: SessionDep) -> SubmissionEntry:
    submission_entry = SubmissionEntry(problem_id=submission.problem_id,
                                       uuid=submission.uuid,
                                       timestamp=submission.timestamp,
                                       score=0,
                                       successful=0)

    max_sid = session.exec(select(func.max(SubmissionEntry.sid))
                           .where(SubmissionEntry.problem_id == submission.problem_id)
                           .where(SubmissionEntry.uuid == submission.uuid)).first()

    code_handler(submission.code)

    if max_sid is not None:
        submission_entry.sid = max_sid + 1
    else:
        submission_entry.sid = 0

    add_commit_refresh(submission_entry, session)

    return submission_entry


@router.get("/submissions/")
async def read_submission(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[SubmissionEntry]:
    submissions = session.exec(select(SubmissionEntry).offset(offset).limit(limit)).all()
    return submissions


@router.get("/api/health", status_code=200)
async def health_check():
    return {"status": "ok", "message": "DB service is running"}
