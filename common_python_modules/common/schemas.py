"""
schemas.py

Defines Pydantic models for the gateway. These mirror what the
DB microservice's /users/ endpoints expect and return.
"""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from common.languages import Language
from common.typing import ErrorReason, PermissionLevel, Difficulty


class ErrorResponse(BaseModel):
    """Individual error details."""

    type: str = Field(description="Error type identifier")
    description: str = Field(description="Human-readable error message")


class JWTokenData(BaseModel):
    """Schema of information stored in JSON Web Token.
    Uuid stored in str as UUID is not JSON serialisable."""

    uuid: str
    username: str
    permission_level: PermissionLevel = PermissionLevel.USER
    avatar_id: int


class TokenResponse(BaseModel):
    """DB should: create and sign a token (JWT?) after successful login, this Schema
    relays the token to the webserver."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class JWTPayload(BaseModel):
    """Schema to communicate JWT payload information containing user authentication data."""

    uuid: UUID
    username: str
    permission: str
    exp: int
    avatar_id: int


class RegisterRequest(BaseModel):
    """Schema to communicate newly created user from Interface to the DB handler."""

    username: str = Field()
    email: str = Field()
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]
    permission_level: PermissionLevel = PermissionLevel.USER


class LoginRequest(BaseModel):
    """Schema to communicate user attempting login from Interface to DB handler."""

    username: str
    password: str


class LeaderboardRequest(BaseModel):
    """Schema to communicate the leaderboard request the Interface to the DB handler."""

    problem_id: int
    first_row: int
    last_row: int


class UserScore(BaseModel):
    """Schema to communicate leaderboard entry from DB handler to the Interface."""

    username: str
    score: float


class LeaderboardResponse(BaseModel):
    """Schema to communicate the leaderboard from DB handler to the Interface."""

    problem_id: int = Field()
    problem_name: str = Field()
    problem_language: Language = Field()
    problem_difficulty: Difficulty = Field()
    scores: list[UserScore] = Field()


class ProblemDetailsResponse(BaseModel):
    """Schema to communicate problem from DB handler to Interface."""

    problem_id: int = Field()
    name: str = Field(max_length=64)
    language: Language = Field()
    difficulty: Difficulty = Field()
    tags: list[str] = Field()
    short_description: str = Field(max_length=256)
    long_description: str = Field(max_length=8096)
    template_code: str = Field(max_length=2048)
    submission_id: UUID | None = None
    wrappers: list[list[str]] = Field()


class ProblemRequest(BaseModel):
    """Schema to communicate problem request by ID from Interface to DB handler."""

    problem_id: int = Field()


class SubmissionRequest(BaseModel):
    """Schema to communicate submission from Interface to the DB handler."""

    problem_id: int = Field()
    language: Language = Field()
    code: str = Field()


class SubmissionMetadata(BaseModel):
    """
    Schema to communicate submission metadata from DB handler to Interface.
    Retrieves all short data; doesn't include code and (often lengthy) error messages.
    """

    submission_uuid: UUID
    problem_id: int
    user_uuid: UUID
    language: Language
    runtime_ms: float
    mem_usage_mb: float
    energy_usage_kwh: float
    timestamp: float
    executed: bool
    successful: bool
    error_reason: ErrorReason | None


class SubmissionResult(BaseModel):
    """Schema to communicate submission result from engine to DB handler."""

    submission_uuid: UUID = Field()
    runtime_ms: float = Field()
    mem_usage_mb: float = Field()
    energy_usage_kwh: float = Field()
    successful: bool = Field()
    error_reason: ErrorReason | None = Field()
    error_msg: str | None = Field()


class SubmissionFull(BaseModel):
    """Retrieves all data about a submission."""

    submission_uuid: UUID
    problem_id: int
    user_uuid: UUID
    language: Language
    runtime_ms: float
    mem_usage_mb: float
    energy_usage_kwh: float
    timestamp: float
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
    timestamp: float = Field()
    code: str = Field()


class SubmissionCreateResponse(BaseModel):
    """Schema to communicate the submission id back to the frontend."""

    submission_uuid: UUID = Field()


class SubmissionResponse(BaseModel):
    """Schema to communicate submission from DB handler to the Interface."""

    error: str | list[str] | None = Field()
    description: str = Field()
    tests_passed: int | None = Field()
    tests_failed: int | None = Field()
    cpu_time: float | None = Field()


class SubmissionRetrieveRequest(BaseModel):
    """Schema to communicate submission retrieve request internally for the DB handler."""

    problem_id: int = Field()
    user_uuid: UUID = Field()
    language: Language = Field()


class AddProblemRequest(BaseModel):
    """Schema to communicate new problem creation request from Interface to DB handler."""

    name: str
    language: Language
    difficulty: Difficulty
    tags: list[str]
    short_description: str
    long_description: str
    template_code: str
    wrappers: list[list[str]]


class AddProblemResponse(BaseModel):
    """Schema to communicate request for a problem by problem-id."""

    problem_id: int = Field()


class AddProblemRequestDev(BaseModel):
    """Schema to communicate new problem creation request from Interface to DB handler.
    Has a hardcoded problem_id and does not need wrappers and templates"""

    name: str
    problem_id: int
    language: Language
    difficulty: Difficulty
    tags: list[str]
    short_description: str
    long_description: str


class UserGet(BaseModel):
    """Schema to communicate user from DB handler to Interface."""

    uuid: UUID
    username: str
    email: str
    permission_level: PermissionLevel = PermissionLevel.USER
    avatar_id: int
    private: bool


class LeaderboardEntryGet(BaseModel):
    """Schema to communicate leaderboard entry from DB handler to the Interface."""

    username: str
    total_score: int
    problems_solved: int
    # rank: int # Optional, can be calculated client side


class LeaderboardGet(BaseModel):
    """Schema to communicate the leaderboard from DB handler to the Interface."""

    entries: list[LeaderboardEntryGet]


class ProblemMetadata(BaseModel):
    """Short summary of a problem, used in problems list."""

    problem_id: int = Field()
    name: str = Field()
    difficulty: Difficulty = Field()
    short_description: str = Field()


class ProblemAllRequest(BaseModel):
    limit: int | None = Field(default=100)


class ProblemsListResponse(BaseModel):
    """Schema to return a list of problems + total count."""

    total: int = Field()
    problems: list[ProblemMetadata] = Field()


class SettingUpdateRequest(BaseModel):
    """Schema to communicate updated field from client to db."""

    user_uuid: UUID = Field()
    key: str = Field()
    value: str = Field()
