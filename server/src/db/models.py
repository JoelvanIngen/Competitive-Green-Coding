from sqlmodel import SQLModel, Field

#TODO: Add relationships and foreignkeys

class Users(SQLModel, table=True):
    uuid: int = Field(primary_key=True, index=True)
    username: str = Field(max_length=32, index=True)
    email: str = Field(max_length=64, index=True)
    password_hash: str = Field() #TODO: assign max_length once hashing-algo decided


class Problems(SQLModel, table=True):
    problem_id: int = Field(primary_key=True, index=True)
    tags: int = Field()
    description: str = Field(max_length=256)

class Submissions(SQLModel, table=True):
    sid: int = Field(primary_key=True, index=True)
    problem_id: int = Field(index=True)
    uuid: int = Field(index=True)
    score: int = Field()
    timestamp: int = Field()
    successful: bool = Field()