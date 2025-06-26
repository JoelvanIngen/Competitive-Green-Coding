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

from sqlmodel import (
    Column,
    Field,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    Relationship,
    SQLModel,
)

from common.languages import Language
from common.schemas import PermissionLevel
from common.typing import Difficulty, ErrorReason


class UserEntry(SQLModel, table=True):
    """
    Schema to store user data in the database.
    """

    uuid: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    username: str = Field(max_length=32, index=True, unique=True)
    email: str = Field(max_length=64, index=True)
    hashed_password: bytes = Field()
    permission_level: PermissionLevel = Field()
    private: bool = False  # by default
    avatar_id: int = 0

    # Relationship: One user can have multiple submissions
    submissions: List["SubmissionEntry"] = Relationship(back_populates="user")


class ProblemEntry(SQLModel, table=True):
    """
    Schema to store problem data in the database.
    """

    problem_id: int = Field(primary_key=True, index=True)
    name: str = Field()
    language: Language = Field()
    difficulty: Difficulty = Field()
    short_description: str = Field(max_length=256)
    long_description: str = Field(max_length=8096)

    # Relationship: One problem can have multiple submissions
    submissions: List["SubmissionEntry"] = Relationship(
        back_populates="problem", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    tags: List["ProblemTagEntry"] = Relationship(
        back_populates="problem", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class SubmissionEntry(SQLModel, table=True):
    """
    Schema to store submission data in the database.
    """

    submission_uuid: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    problem_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("problementry.problem_id", ondelete="CASCADE"),
            index=True,
        )
    )
    user_uuid: UUID = Field(foreign_key="userentry.uuid", index=True)
    language: Language = Field()
    runtime_ms: float = Field()
    emmissions_kg: float = Field()
    energy_usage_kwh: float = Field()
    timestamp: float = Field()
    executed: bool = Field()
    successful: bool | None = Field()
    error_reason: ErrorReason | None = Field()
    error_msg: str | None = Field()

    # Relationships: Each submission belongs to one user and one problem
    user: UserEntry = Relationship(back_populates="submissions")
    problem: ProblemEntry = Relationship(
        back_populates="submissions",
        sa_relationship_kwargs={"passive_deletes": True},
    )


class ProblemTagEntry(SQLModel, table=True):
    problem_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("problementry.problem_id", ondelete="CASCADE"),
            primary_key=True,
            index=True,
        )
    )
    tag: str = Field(primary_key=True, index=True)

    problem: ProblemEntry = Relationship(
        back_populates="tags", sa_relationship_kwargs={"passive_deletes": True}
    )

    __table_args__ = (PrimaryKeyConstraint("problem_id", "tag"),)
