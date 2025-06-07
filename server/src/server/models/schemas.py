"""
schemas.py

Defines Pydantic models for the gateway. These mirror what the
DB microservice's /users/ endpoints expect and return.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints
from uuid import UUID


class UserRegister(BaseModel):
    """Schema to communicate newly created user from Interface to the DB handler."""

    username: str = Field(max_length=32)
    email: str = Field(max_length=64)
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


class UserLogin(BaseModel):
    """Schema to communicate user attempting login from Interface to DB handler."""

    username: str
    password: str


class UserGet(BaseModel):
    """Schema to communicate user from DB handler to Interface."""

    uuid: UUID
    username: str
    email: str


class TokenResponse(BaseModel):
    """DB should: create and sign a token (JWT?) after succesfull login, this Schema
    relays the token to the webserver."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


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

    problem_id: int = Field()
    uuid: UUID = Field()
    timestamp: int = Field()
    code: str = Field()


class SubmissionGet(BaseModel):
    """Schema to communicate submission from DB handler to the Interface."""

    sid: int
    problem_id: int
    uuid: UUID
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
