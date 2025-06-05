import uuid

from sqlmodel import SQLModel, Field, Relationship
from typing import List


class UserEntry(SQLModel, table=True):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    username: str = Field(max_length=32, index=True)
    email: str = Field(max_length=64, index=True)
    password_hash: str = Field()  # TODO: assign max_length once hashing-algo decided

    # Relationship: One user can have multiple submissions
    submissions: List["SubmissionEntry"] = Relationship(back_populates="user")


class ProblemEntry(SQLModel, table=True):
    problem_id: int = Field(primary_key=True, index=True)
    tags: int = Field()
    description: str = Field(max_length=256)

    # Relationship: One problem can have multiple submissions
    submissions: List["SubmissionEntry"] = Relationship(back_populates="problem")


class SubmissionEntry(SQLModel, table=True):
    sid: int = Field(primary_key=True, index=True)
    problem_id: int = Field(foreign_key="problem.problem_id", index=True)
    uid: int = Field(foreign_key="user.id", index=True)
    score: int = Field()
    timestamp: int = Field()
    successful: bool = Field()

    # Relationships: Each submission belongs to one user and one problem
    user: UserEntry = Relationship(back_populates="submissions")
    problem: ProblemEntry = Relationship(back_populates="submissions")
