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

from sqlmodel import Field, Relationship, SQLModel

from db.models.schemas import PermissionLevel


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
    tags: int = Field()
    short_description: str = Field(max_length=256)
    long_description: str = Field(max_length=8096)
    template_code: str = Field(max_length=2048)

    # Relationship: One problem can have multiple submissions
    submissions: List["SubmissionEntry"] = Relationship(back_populates="problem")


class SubmissionEntry(SQLModel, table=True):
    """
    Schema to store submission data in the database.
    """

    sid: int = Field(primary_key=True, index=True)
    problem_id: int = Field(foreign_key="problementry.problem_id", index=True)
    uuid: UUID = Field(foreign_key="userentry.uuid", index=True)
    runtime_ms: int = Field()
    timestamp: int = Field()
    successful: bool = Field()
    score: int = Field()

    # Relationships: Each submission belongs to one user and one problem
    user: UserEntry = Relationship(back_populates="submissions")
    problem: ProblemEntry = Relationship(back_populates="submissions")
