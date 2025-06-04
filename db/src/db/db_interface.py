from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, SQLModel, create_engine, select

from db.models import User, Problem, Submission


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
def create_user(user: User, session: SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@app.get("/users/{user_id}")
def read_user(user_id: int, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/problems/")
def create_problem(problem: Problem, session: SessionDep) -> Problem:
    session.add(problem)
    session.commit()
    session.refresh(problem)
    return problem


@app.get("/problems/")
def read_problems(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Problem]:
    problems = session.exec(select(Problem).offset(offset).limit(limit)).all()
    return problems


@app.get("/problems/{problem_id}")
def read_problem(problem_id: int, session: SessionDep) -> Problem:
    problem = session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@app.post("/submissions/")
def create_submission(submission: Submission, session: SessionDep) -> Submission:
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission


@app.get("/submissions/")
def read_submission(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Submission]:
    submissions = session.exec(select(Submission).offset(offset).limit(limit)).all()
    return submissions


@app.get("/submissions/{problem_id}/{user_id}/last_sid/")
def get_last_sid(problem_id: int, user_id: int, session: SessionDep) -> int:
    sid = session.exec(select(Submission.sid)
                       .where(Submission.uuid == user_id)
                       .where(Submission.problem_id == problem_id)).first()
    if not sid:
        return 0
    return sid
