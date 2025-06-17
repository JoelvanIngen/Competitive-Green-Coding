from pydantic import BaseModel, Field


class ProblemRequest(BaseModel):
    """Schema to communicate request for a problem by problem-id."""

    problem_id: int = Field()


class AddProblemRequest(BaseModel):
    """Schema to communicate request for adding a problem."""

    name: str = Field()
    language: str = Field()
    difficulty: str = Field()
    tags: str = Field()
    short_description: str = Field()
    long_description: str = Field()
    template_code: str = Field()
