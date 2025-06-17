"""
schemas.py

Defines Pydantic models for the gateway. These mirror what the
DB microservice's /users/ endpoints expect and return.
"""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from common.schemas import PermissionLevel


# TODO: check if correct
class ErrorResponse(BaseModel):
    """Schema to communicate error responses from DB handler to Interface."""

    error_type: str | list[str] = Field()
    description: str = Field()


class RegisterErrorResponse(BaseModel):
    """Schema to communicate registration error responses from DB handler to Interface."""

    error_type: str | list[str] = Field()
    description: str = Field()


class JWTPayload(BaseModel):
    """Schema to communicate JWT payload information containing user authentication data."""

    uuid: UUID
    username: str
    permission: str
    exp: int


class LeaderboardRequest(BaseModel):
    """Schema to communicate the leaderboard request the Interface to the DB handler."""

    problem_id: int  # TODO: change to UUID?
    first_row: int
    last_row: int


class UserScore(BaseModel):
    """Schema to communicate leaderboard entry from DB handler to the Interface."""

    username: str
    score: int
    # rank: int # Optional, can be calculated client side


class LeaderboardErrorResponse(BaseModel):
    """Schema to communicate leaderboard error responses from DB handler to Interface."""

    error: str = Field()


# TODO: add to Openai
class ProblemRequest(BaseModel):
    """Schema to communicate problem request by ID from Interface to DB handler."""

    problem_id: int = Field()  # TODO: change to UUID?


class ProblemErrorResponse(BaseModel):
    """Schema to communicate problem-related error responses from DB handler to Interface."""

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
    """Schema to communicate submission-related error responses from DB handler to Interface."""

    error: str = Field()


class AdminErrorResponse(BaseModel):
    """Schema to communicate admin operation error responses from DB handler to Interface."""

    error: str = Field()
    description: str = Field()


class AdminDetailedErrorResponse(BaseModel):
    """Schema to communicate detailed admin error responses from DB handler to Interface."""

    error: str = Field()


class AddProblemRequest(BaseModel):
    """Schema to communicate new problem creation request from Interface to DB handler."""

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
