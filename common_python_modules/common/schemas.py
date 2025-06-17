"""
schemas.py

Defines Pydantic models for the gateway. These mirror what the
DB microservice's /users/ endpoints expect and return.
"""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from common.typing import ErrorReason, Language, PermissionLevel


class JWTokenData(BaseModel):
    """Schema of information stored in JSON Web Token.
    Uuid stored in str as UUID is not JSON serialisable."""

    uuid: str
    username: str
    permission_level: PermissionLevel = PermissionLevel.USER


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
    """DB should: create and sign a token (JWT?) after successful login, this Schema
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


class SubmissionMetadata(BaseModel):
    """
    Schema to communicate submission metadata from DB handler to Interface.
    Retrieves all short data; doesn't include code and (often lengthy) error messages.
    """

    submission_uuid: UUID
    problem_id: int
    user_uuid: UUID
    language: Language
    runtime_ms: int
    mem_usage_mb: float
    timestamp: int
    executed: bool
    successful: bool
    error_reason: ErrorReason | None


class SubmissionFull(BaseModel):
    """Retrieves all data about a submission."""
    submission_uuid: UUID
    problem_id: int
    user_uuid: UUID
    language: Language
    runtime_ms: int
    mem_usage_mb: float
    timestamp: int
    executed: bool
    successful: bool
    error_reason: ErrorReason | None
    error_msg: str | None
    code: str


class SubmissionCreate(BaseModel):
    """Minimal metadata needed to create DB entry for submission and to execute code"""

    submission_uuid: UUID = Field()
    problem_id: int = Field()
    user_uuid: UUID = Field()
    language: Language = Field()
    timestamp: int = Field()
    code: str = Field()


class SubmissionResult(BaseModel):
    """Schema to communicate submission result from engine to DB handler."""

    submission_uuid: UUID = Field()
    runtime_ms: int = Field()
    mem_usage_mb: float = Field()
    successful: bool = Field()
    error_reason: ErrorReason | None = Field()
    error_msg: str | None = Field()


class LeaderboardEntryGet(BaseModel):
    """Schema to communicate leaderboard entry from DB handler to the Interface."""

    username: str
    total_score: int
    problems_solved: int
    # rank: int # Optional, can be calculated client side


class LeaderboardGet(BaseModel):
    """Schema to communicate the leaderboard from DB handler to the Interface."""

    entries: list[LeaderboardEntryGet]
