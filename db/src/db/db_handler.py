from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, SQLModel, create_engine, select, func
import uuid

from db.models.db_schemas import UserEntry, ProblemEntry, SubmissionEntry
from db.models.schemas import UserGet, UserPost, ProblemGet, ProblemPost, \
    SubmissionGet, SubmissionPost, LeaderboardEntryGet, LeaderboardGet


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

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/users/")
def create_user(user: UserPost, session: SessionDep) -> UserEntry:
    user_entry = UserEntry(username=user.username, email=user.email,
                           password_hash=user.password_hash)
    user_entry.uid = str(uuid.uuid4())

    session.add(user_entry)
    session.commit()
    session.refresh(user_entry)

    return user_entry


# WARNING: for development purposes only
@app.get("/users/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[UserEntry]:
    users = session.exec(select(UserEntry).offset(offset).limit(limit)).all()
    return users


@app.get("/users/{username}")
def read_user(username: str, session: SessionDep) -> UserGet:
    user = session.exec(select(UserEntry).where(UserEntry.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_get = UserGet(uuid=user.uid, username=user.username, email=user.email)

    return user_get


@app.get("/users/leaderboard")
def get_leaderboard(session: SessionDep, offset: int = 0) -> LeaderboardGet:

    query = (
        select(
            UserEntry.username,
            func.sum(SubmissionEntry.score).label("total_score"),
            func.count(func.distinct(SubmissionEntry.problem_id)).label("problems_solved")
        )
        .select_from(SubmissionEntry)
        .join(UserEntry, SubmissionEntry.uid == UserEntry.uid)
        .where(SubmissionEntry.successful == True)
        .group_by(SubmissionEntry.uid, UserEntry.username)
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


# @app.post("/problems/")
# def create_problem(problem: ProblemEntry, session: SessionDep) -> ProblemEntry:
#     session.add(problem)
#     session.commit()
#     session.refresh(problem)
#     return problem


# @app.get("/problems/")
# def read_problems(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100,
# ) -> list[ProblemEntry]:
#     problems = session.exec(select(ProblemEntry).offset(offset).limit(limit)).all()
#     return problems


# @app.get("/problems/{problem_id}")
# def read_problem(problem_id: int, session: SessionDep) -> ProblemEntry:
#     problem = session.get(ProblemEntry, problem_id)
#     if not problem:
#         raise HTTPException(status_code=404, detail="Problem not found")
#     return problem


# @app.post("/submissions/")
# def create_submission(submission: SubmissionEntry, session: SessionDep) -> SubmissionEntry:
#     session.add(submission)
#     session.commit()
#     session.refresh(submission)
#     return submission


# @app.get("/submissions/")
# def read_submission(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100,
# ) -> list[SubmissionEntry]:
#     submissions = session.exec(select(SubmissionEntry).offset(offset).limit(limit)).all()
#     return submissions


# @app.get("/submissions/{problem_id}/{user_id}/last_sid/")
# def get_last_sid(problem_id: int, user_id: int, session: SessionDep) -> int:
#     sid = session.exec(select(SubmissionEntry.sid)
#                        .where(SubmissionEntry.uuid == user_id)
#                        .where(SubmissionEntry.problem_id == problem_id)).first()
#     if not sid:
#         return 0
#     return sid
