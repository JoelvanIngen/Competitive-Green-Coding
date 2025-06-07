from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from typing import List


class UserEntry(SQLModel, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    username: str = Field(max_length=32, index=True)
    email: str = Field(max_length=64, index=True)
    hashed_password: bytes = Field()

    # Relationship: One user can have multiple submissions
    submissions: List["SubmissionEntry"] = Relationship(back_populates="user")


class ProblemEntry(SQLModel, table=True):
    problem_id: int = Field(primary_key=True, index=True)
    name: str = Field()
    tags: int = Field()
    description: str = Field(max_length=256)

    # Relationship: One problem can have multiple submissions
    submissions: List["SubmissionEntry"] = Relationship(back_populates="problem")


class SubmissionEntry(SQLModel, table=True):
    sid: int = Field(primary_key=True, index=True)
    problem_id: int = Field(foreign_key="problementry.problem_id", index=True)
    uuid: UUID = Field(foreign_key="userentry.uuid", index=True)
    score: int = Field()
    timestamp: int = Field()
    successful: bool = Field()  # TODO: this gets automatically converted to int?

    # Relationships: Each submission belongs to one user and one problem
    user: UserEntry = Relationship(back_populates="submissions")
    problem: ProblemEntry = Relationship(back_populates="submissions")
