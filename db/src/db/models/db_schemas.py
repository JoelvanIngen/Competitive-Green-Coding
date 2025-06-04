from sqlmodel import SQLModel, Field

# TODO: Add relationships and foreignkeys


class UserEntry(SQLModel, table=True):
    uuid: str = Field(primary_key=True, index=True)
    username: str = Field(max_length=32, index=True)
    email: str = Field(max_length=64, index=True)
    password_hash: str = Field()  # TODO: assign max_length once hashing-algo decided


class ProblemEntry(SQLModel, table=True):
    problem_id: int = Field(primary_key=True, index=True)
    name: str = Field(max_length=64)
    tags: int = Field()
    description: str = Field(max_length=256)


class SubmissionEntry(SQLModel, table=True):
    sid: int = Field(primary_key=True, index=True)
    problem_id: int = Field(index=True)
    uuid: str = Field(index=True)
    score: int = Field()
    timestamp: int = Field()
    successful: bool = Field()
