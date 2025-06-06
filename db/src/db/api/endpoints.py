from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, SQLModel, create_engine, select, func
import uuid

from models.db_schemas import UserEntry, ProblemEntry, SubmissionEntry
from models.schemas import UserGet, UserPost, ProblemGet, ProblemPost, \
    SubmissionPost, LeaderboardEntryGet, LeaderboardGet


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


@router.post("/users/")
def create_user(user: UserPost, session: SessionDep) -> UserEntry:
    user_entry = UserEntry(username=user.username, email=user.email,
                           password_hash=user.password_hash)
    user_entry.uuid = uuid.uuid4()

    session.add(user_entry)
    session.commit()
    session.refresh(user_entry)

    return user_entry


# WARNING: for development purposes only
@router.get("/users/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=1000)] = 1000,
) -> list[UserEntry]:
    users = session.exec(select(UserEntry).offset(offset).limit(limit)).all()
    return users


@router.get("/users/{username}")
def read_user(username: str, session: SessionDep) -> UserGet:
    user = session.exec(
        select(UserEntry).where(UserEntry.username == username)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_get = UserGet(
        uuid=user.uuid,
        username=user.username,
        email=user.email
    )

    return user_get


@router.get("/leaderboard")
def get_leaderboard(session: SessionDep, offset: int = 0) -> LeaderboardGet:

    query = (
        select(
            UserEntry.username,
            func.sum(SubmissionEntry.score).label("total_score"),
            func.count(func.distinct(SubmissionEntry.problem_id)).label(
                "problems_solved"
            )
        )
        .select_from(SubmissionEntry)
        .join(UserEntry, SubmissionEntry.uuid == UserEntry.uuid)
        .where(SubmissionEntry.successful == 1)
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


def translate_tags_to_bitmap(tags: list[str]) -> int:
    bitmap = 0

    for tag in tags:
        if tag == "C":
            bitmap += 1 << 0
        elif tag == "python":
            bitmap += 1 << 1

    return bitmap


def translate_bitmap_to_tags(bitmap: int) -> list[str]:
    tags = []
    possible_tags = ["C", "python"]

    for i in range(len(bin(bitmap)) - 2):
        if (bitmap >> i) % 2 == 1:
            tags.append(possible_tags[i])

    return tags


@router.post("/problems/")
def create_problem(problem: ProblemPost, session: SessionDep) -> ProblemEntry:
    problem_entry = ProblemEntry(
        name=problem.name, description=problem.description
    )
    problem_entry.tags = translate_tags_to_bitmap(problem.tags)

    max_problem_id = session.exec(func.max(ProblemEntry.problem_id)).scalar()

    if max_problem_id is not None:
        problem_entry.problem_id = max_problem_id + 1
    else:
        problem_entry.problem_id = 0

    session.add(problem_entry)
    session.commit()
    session.refresh(problem_entry)

    return problem_entry


@router.get("/problems/")
def read_problems(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[ProblemGet]:
    problems = session.exec(select(ProblemEntry)
                            .offset(offset).limit(limit)).all()

    problem_gets = []
    for problem in problems:
        problem_get = ProblemGet(
            problem_id=problem.problem_id,
            name=problem.name,
            description=problem.description,
            tags=[]
        )
        problem_get.tags = translate_bitmap_to_tags(problem.tags)
        problem_gets.append(problem_get)

    return problem_gets


@router.get("/problems/{problem_id}")
def read_problem(problem_id: int, session: SessionDep) -> ProblemGet:
    problem = session.get(ProblemEntry, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    problem_get = ProblemGet(
        problem_id=problem.problem_id,
        name=problem.name,
        description=problem.description,
        tags=[]
    )

    problem_get.tags = translate_bitmap_to_tags(problem.tags)

    return problem_get


def code_handler(code: str):
    ...


@router.post("/submissions/")
def create_submission(submission: SubmissionPost,
                      session: SessionDep) -> SubmissionEntry:
    submission_entry = SubmissionEntry(problem_id=submission.problem_id,
                                       uuid=submission.uuid,
                                       score=submission.score,
                                       timestamp=submission.timestamp,
                                       successful=submission.successful,
                                       code=submission.code)

    # Get the maximum sid across all submissions
    max_sid = session.exec(func.max(SubmissionEntry.sid)).scalar()

    code_handler(submission.code)

    if max_sid is not None:
        submission_entry.sid = max_sid + 1
    else:
        submission_entry.sid = 0

    session.add(submission_entry)
    session.commit()
    session.refresh(submission_entry)

    return submission_entry


@router.get("/submissions/")
def read_submission(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[SubmissionEntry]:
    submissions = session.exec(
        select(SubmissionEntry).offset(offset).limit(limit)
    ).all()
    return submissions
