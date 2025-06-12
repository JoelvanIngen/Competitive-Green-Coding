from pydantic import BaseModel, Field


class ProblemRequest(BaseModel):
    """Schema to communicate request for a problem by problem-id."""
    problem_id: int = Field()
