"""
schemas.py

Defines Pydantic models for the gateway. These mirror what the
DB microservice’s `/users/` endpoints expect and return.
"""

from pydantic import BaseModel, Field


class UserPost(BaseModel):
    """Schema to communicate newly created user from Interface to the DB handler."""

    username: str = Field(max_length=32, index=True)
    email: str = Field(max_length=64, index=True)
    password: constr(
        min_length=8,
        max_length=128,
    )
    # TODO: assign max_length once hashing-algo decided


class UserGet(BaseModel):
    """Schema to communicate user from DB handler to Interface."""

    uuid: int
    username: str
    email: str


class ProblemPost(BaseModel):
    """Schema to communicate created problem from Interface to the DB handler."""

    name: str = Field(max_length=64)
    tags: list[str] = Field()
    description: str = Field(max_length=256)


class ProblemGet(BaseModel):
    """Schema to communicate problem from DB handler to Interface."""

    problem_id: int = Field()
    name: str = Field(max_length=64)
    tags: list[str] = Field()
    description: str = Field(max_length=256)


class SubmissionPost(BaseModel):
    """Schema to communicate submission from Interface to the DB handler."""

    problem_id: int = Field(index=True)
    uuid: str = Field(index=True)
    timestamp: int = Field()
    code: str = Field()


class SubmissionGet(BaseModel):
    """Schema to communicate submission from DB handler to the Interface."""

    sid: int
    problem_id: int
    uuid: int
    score: int
    timestamp: int
    successful: bool
    code: str


class LeaderboardEntryGet(BaseModel):
    """Schema to communicate leaderboard entry from DB handler to the Interface."""

    username: str
    total_score: int
    problems_solved: int
    # rank: int # Optional, can be calculated client side


class LeaderboardGet(BaseModel):
    """Schema to communicate the leaderboard from DB handler to the Interface."""

    entries: list[LeaderboardEntryGet]
