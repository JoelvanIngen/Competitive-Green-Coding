"""
schemas.py

Defines Pydantic models for the gateway. These mirror what the
DB microservice's /users/ endpoints expect and return.
"""

from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints


class PermissionLevel(str, Enum):
    """Permission level enumeration used for user accounts."""

    USER = "user"
    ADMIN = "admin"


class UserRegister(BaseModel):
    """Schema to communicate newly created user from Interface to the DB handler."""

    username: str = Field(max_length=32)
    email: str = Field(max_length=64)
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]
    permission_level: PermissionLevel = PermissionLevel.USER


class UserLogin(BaseModel):
    """Schema to communicate user attempting login from Interface to DB handler."""

    username: str
    password: str


class UserGet(BaseModel):
    """Schema to communicate user from DB handler to Interface."""

    uuid: UUID
    username: str
    email: str
    permission_level: PermissionLevel = PermissionLevel.USER


class TokenResponse(BaseModel):
    """DB should: create and sign a token (JWT?) after succesfull login, this Schema
    relays the token to the webserver."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class ProblemPost(BaseModel):
    """Schema to communicate created problem from Interface to the DB handler."""

    name: str = Field(max_length=64)
    language: str = Field()
    difficulty: str = Field()
    tags: list[str] = Field()
    short_description: str = Field(max_length=256)
    long_description: str = Field(max_length=8096)
    template_code: str = Field(max_length=2048)


class ProblemGet(BaseModel):
    """Schema to communicate problem from DB handler to Interface."""

    problem_id: int = Field()
    name: str = Field(max_length=64)
    language: str = Field()
    difficulty: str = Field()
    tags: list[str] = Field()
    short_description: str = Field(max_length=256)
    long_description: str = Field(max_length=8096)
    template_code: str = Field(max_length=2048)


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
