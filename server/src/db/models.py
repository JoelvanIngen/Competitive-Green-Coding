from sqlmodel import SQLModel, Field, Relationship
from typing import List


class User(SQLModel, table=True):
    uuid: int = Field(primary_key=True, index=True)
    username: str = Field(max_length=32, index=True)
    email: str = Field(max_length=64, index=True)
    password_hash: str = Field()  # TODO: assign max_length once hashing-algo decided

    # Relationship: One user can have multiple submissions
    submissions: List["Submission"] = Relationship(back_populates="user")


class Problem(SQLModel, table=True):
    problem_id: int = Field(primary_key=True, index=True)
    tags: int = Field()
    description: str = Field(max_length=256)

    # Relationship: One problem can have multiple submissions
    submissions: List["Submission"] = Relationship(back_populates="problem")


class Submission(SQLModel, table=True):
    sid: int = Field(primary_key=True, index=True)
    problem_id: int = Field(foreign_key="problem.problem_id", index=True)
    uuid: int = Field(foreign_key="user.uuid", index=True)
    score: int = Field()
    timestamp: int = Field()
    successful: bool = Field() #TODO: this gets automatically converted to int?

    # Relationships: Each submission belongs to one user and one problem
    user: User = Relationship(back_populates="submissions")
    problem: Problem = Relationship(back_populates="submissions")
