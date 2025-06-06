from pydantic import BaseModel, Field
from uuid import UUID


class UserPost(BaseModel):
    """Schema to communicate newly created user from Interface to the DB handler.
    """
    username: str = Field(max_length=32, index=True)
    email: str = Field(max_length=64, index=True)
    password_hash: str = Field()  # TODO: assign max_length once hashing-algo decided


class UserGet(BaseModel):
    """Schema to communicate user from DB handler to Interface.
    """
    uuid: UUID
    username: str
    email: str


class ProblemPost(BaseModel):
    """Schema to communicate created problem from Interface to the DB handler.
    """
    name: str = Field(max_length=64)
    tags: list[str] = Field()
    description: str = Field(max_length=256)


class ProblemGet(BaseModel):
    """Schema to communicate problem from DB handler to Interface.
    """
    problem_id: int = Field()
    name: str = Field(max_length=64)
    tags: list[str] = Field()
    description: str = Field(max_length=256)


class SubmissionPost(BaseModel):
    """Schema to communicate submission from Interface to the DB handler.
    """
    problem_id: int = Field(index=True)
    uuid: UUID = Field(index=True)
    score: int = Field()
    timestamp: int = Field()
    successful: bool = Field()
    code: str = Field()


class SubmissionGet(BaseModel):
    """Schema to communicate submission from DB handler to the Interface.
    """
    sid: int
    problem_id: int
    uuid: UUID
    score: int
    timestamp: int
    successful: bool
    code: str


class LeaderboardEntryGet(BaseModel):
    """Schema to communicate leaderboard entry from DB handler to the Interface.
    """
    username: str
    total_score: int
    problems_solved: int
    # rank: int # Optional, can be calculated client side


class LeaderboardGet(BaseModel):
    """Schema to communicate the leaderboard from DB handler to the Interface."""
    entries: list[LeaderboardEntryGet]
