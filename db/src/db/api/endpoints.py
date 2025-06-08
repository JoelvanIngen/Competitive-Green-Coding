"""
Module containing API endpoints and routing logic.
- Should perform as little action as possible
- All endpoint functions should call an identically-named function from the `actions` submodule,
  to keep this file's footprint as small as possible (otherwise you'll be scrolling for half an
  hour just trying to find a specific function)
"""

from typing import Annotated

from fastapi import APIRouter, Query
from sqlmodel import select

from db.api.modules import actions
from db.api.modules.bitmap_translator import translate_bitmap_to_tags
from db.engine import ops, queries
from db.models.convert import db_problem_to_problem_get, db_user_to_user
from db.models.db_schemas import ProblemEntry, SubmissionEntry, UserEntry
from db.models.schemas import (
    LeaderboardGet,
    ProblemGet,
    ProblemPost,
    SubmissionPost,
    TokenResponse,
    UserGet,
    UserLogin,
    UserRegister,
)
from db.typing import SessionDep

router = APIRouter()


def code_handler(code: str) -> None:
    raise NotImplementedError(code)  # Use variable code so pylint doesn't warn


@router.post("/auth/register/")
async def register_user(user: UserRegister, session: SessionDep) -> UserGet:
    return actions.register_user(session, user)


@router.post("/auth/login/")
async def login_user(login: UserLogin, session: SessionDep) -> TokenResponse:
    return actions.login_user(session, login)


@router.post("/users/me/")
async def lookup_current_user(token: TokenResponse) -> UserGet:
    return actions.lookup_current_user(token)


# WARNING: for development purposes only
@router.get("/users/")
async def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=1000)] = 1000,
) -> list[UserEntry]:

    # TODO: We should put this is a 'testing' submodule if we want to keep this
    #       or even better, put this as a standard test function in tests/unit/api/endpoints.py

    users = session.exec(select(UserEntry).offset(offset).limit(limit)).all()
    return list(users)


@router.get("/users/{username}")
async def read_user(username: str, session: SessionDep) -> UserGet:
    return actions.lookup_user(session, username)


@router.get("/leaderboard")
async def get_leaderboard(session: SessionDep) -> LeaderboardGet:
    return actions.get_leaderboard(session)


@router.post("/problems/")
async def create_problem(problem: ProblemPost, session: SessionDep) -> None:
    actions.create_problem(session, problem)


@router.get("/problems/")
async def read_problems(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[ProblemGet]:

    return actions.read_problems(session, offset, limit)


@router.get("/problems/{problem_id}")
async def read_problem(problem_id: int, session: SessionDep) -> ProblemGet:
    return actions.read_problem(session, problem_id)


@router.post("/submissions/")
async def create_submission(submission: SubmissionPost, session: SessionDep):
    return actions.create_submission(session, submission)


@router.get("/submissions/")
async def read_submissions(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
) -> list[SubmissionEntry]:

    submissions = session.exec(select(SubmissionEntry).offset(offset).limit(limit)).all()
    return list(submissions)


@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "message": "DB service is running"}
