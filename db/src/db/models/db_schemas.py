"""
db_schemas.py

Contains schemas used by the db handler to store data into the database.

UserEntry(__uuid__, username, email, hashed_password, permission_level)
ProblemEntry(__problem_id__, name, language, difficulty, tags, short_description, long_description,
             template_code)
SubmissonEntry(__sid__, __problem_id__ -> ProblemEntry, __uuid__ -> UserEntry, score, timestamp,
               successful)
"""

from typing import List
from uuid import UUID, uuid4

from sqlmodel import Field, PrimaryKeyConstraint, Relationship, SQLModel

from common.languages import Language
from common.schemas import PermissionLevel
from common.typing import ErrorReason


class UserEntry(SQLModel, table=True):
    """
    Schema to store user data in the database.
    """

    uuid: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    username: str = Field(max_length=32, index=True, unique=True)
    email: str = Field(max_length=64, index=True)
    hashed_password: bytes = Field()
    permission_level: PermissionLevel = Field()

    # Relationship: One user can have multiple submissions
    submissions: List["SubmissionEntry"] = Relationship(back_populates="user")


class ProblemEntry(SQLModel, table=True):
    """
    Schema to store problem data in the database.
    """

    problem_id: int = Field(primary_key=True, index=True)
    name: str = Field()
    language: str = Field()
    difficulty: str = Field()
    short_description: str = Field(max_length=256)
    long_description: str = Field(max_length=8096)
    template_code: str = Field(max_length=2048)

    # Relationship: One problem can have multiple submissions
    submissions: List["SubmissionEntry"] = Relationship(back_populates="problem")
    tags: List["ProblemTagEntry"] = Relationship(back_populates="problem")


class SubmissionEntry(SQLModel, table=True):
    """
    Schema to store submission data in the database.
    """

    submission_uuid: UUID = Field(primary_key=True, index=True)
    problem_id: int = Field(foreign_key="problementry.problem_id", index=True)
    user_uuid: UUID = Field(foreign_key="userentry.uuid", index=True)
    language: Language = Field()
    runtime_ms: int = Field()
    mem_usage_mb: float = Field()
    timestamp: int = Field()
    executed: bool = Field()
    successful: bool | None = Field()
    error_reason: ErrorReason | None = Field()
    error_msg: str | None = Field()

    # Relationships: Each submission belongs to one user and one problem
    user: UserEntry = Relationship(back_populates="submissions")
    problem: ProblemEntry = Relationship(back_populates="submissions")


class ProblemTagEntry(SQLModel, table=True):
    problem_id: int = Field(primary_key=True, foreign_key="problementry.problem_id", index=True)
    tag: str = Field(primary_key=True, index=True)

    problem: ProblemEntry = Relationship(back_populates="tags")

    __table_args__ = (PrimaryKeyConstraint('problem_id', 'tag'))
