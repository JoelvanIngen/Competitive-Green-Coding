"""
schemas.py

Defines Pydantic models for the gateway. These mirror what the
DB microservice's /users/ endpoints expect and return.
"""

from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints


# TODO: check if correct
class ErrorResponse(BaseModel):
    """"""

    error_type: str | list[str] = Field()
    description: str = Field()


class RegisterErrorResponse(BaseModel):
    """"""

    error_type: str | list[str] = Field()
    description: str = Field()


# TODO: docs / still used?
class PermissionLevel(str, Enum):
    """Permission level enumeration used for user accounts."""

    USER = "user"
    ADMIN = "admin"


# TODO: deprecated?
class TokenResponse(BaseModel):
    """DB should: create and sign a token (JWT?) after succesfull login, this Schema
    relays the token to the webserver."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class JWTPayload(BaseModel):
    """"""

    uuid: UUID
    username: str
    permission: str
    exp: int


class RegisterRequest(BaseModel):
    """Schema to communicate newly created user from Interface to the DB handler."""

    username: str = Field(max_length=32)
    email: str = Field(max_length=64)
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]
    permission_level: PermissionLevel = PermissionLevel.USER  # TODO: not specified in OpenAPI doc?


class LoginRequest(BaseModel):
    """Schema to communicate user attempting login from Interface to DB handler."""

    username: str
    password: str


class LeaderboardRequest(BaseModel):
    """Schema to communicate the leaderboard request the Interface to the DB handler. """

    problem_id: int  # TODO: change to UUID?
    first_row: int
    last_row: int


class UserScore(BaseModel):
    """Schema to communicate leaderboard entry from DB handler to the Interface."""

    username: str
    score: int
    # rank: int # Optional, can be calculated client side


class LeaderboardResponse(BaseModel):
    """Schema to communicate the leaderboard from DB handler to the Interface."""

    problem_id: int = Field()  # TODO: change to UUID?
    problem_name: str = Field()
    problem_language: str = Field()
    problem_difficulty: str = Field()
    scores: list[UserScore] = Field()


class LeaderboarqdErrorResponse(BaseModel):
    """"""

    error: str = Field()


# TODO: add to Openai
class ProblemRequest(BaseModel):
    """"""

    problem_id: int = Field()  # TODO: change to UUID?


class ProblemDetailsResponse(BaseModel):
    """Schema to communicate problem from DB handler to Interface."""

    problem_id: int = Field()  # TODO: change to UUID?
    name: str = Field(max_length=64)
    language: str = Field()
    difficulty: str = Field()
    tags: list[str] = Field()
    short_description: str = Field(max_length=256)
    long_description: str = Field(max_length=8096)
    template_code: str = Field(max_length=2048)


class ProblemErrorResponse(BaseModel):
    """"""
    error: str = Field()


class ProblemPost(BaseModel):
    """Schema to communicate created problem from Interface to the DB handler."""

    name: str = Field(max_length=64)
    language: str = Field()
    difficulty: str = Field()
    tags: list[str] = Field()
    short_description: str = Field(max_length=256)
    long_description: str = Field(max_length=8096)
    template_code: str = Field(max_length=2048)


# TODO: more entries here than OpenAPI doc
class SubmissionRequest(BaseModel):
    """Schema to communicate submission from Interface to the DB handler."""

    problem_id: int = Field()  # TODO: change to UUID?
    uuid: UUID = Field()  # TODO: change to UUID?
    timestamp: int = Field()
    code: str = Field()


# TODO: enum in error?
class SubmissionResponse(BaseModel):
    """Schema to communicate submission from DB handler to the Interface."""

    error: str | list[str] | None = Field()
    description: str = Field()
    tests_passed: int | None = Field()
    tests_failed: int | None = Field()
    cpu_time: float | None = Field()


class SubmissionErrorResponse(BaseModel):
    """"""
    error: str = Field()


class AdminErrorResponse(BaseModel):
    """"""
    error: str = Field()
    description: str = Field()


class AdminDetailedErrorResponse(BaseModel):
    """"""
    error: str = Field()


class AddProblemRequest(BaseModel):
    """"""
    name: str
    language: str
    difficulty: str
    tags: list[str]
    short_description: str
    long_description: str
    template_code: str


class AddProblemResponse(BaseModel):
    """Schema to communicate request for a problem by problem-id."""

    problem_id: int = Field()  # TODO: change to UUID?


class AdminProblemsResponse(BaseModel):
    """Schema to communicate admin problems from DB handler to Interface."""

    problems: list[AddProblemRequest] = Field()


class UserGet(BaseModel):
    """Schema to communicate user from DB handler to Interface."""

    uuid: UUID
    username: str
    email: str
    permission_level: PermissionLevel = PermissionLevel.USER
