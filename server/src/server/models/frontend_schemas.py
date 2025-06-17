from enum import Enum

from pydantic import BaseModel, Field


class HTTPErrorTypeDescription(tuple[str, str], Enum):
    """Error type and corresponding description for the problem IDs as determined in
    server/api/README.md."""

    PROB_USERNAME_EXISTS = ("username", "Username already in use")
    PROB_EMAIL_REGISTERED = ("email", "There already exists an account associated to this email")
    PROB_USERNAME_CONSTRAINTS = ("username", "Username does not match constraints")
    PROB_INVALID_EMAIL = ("email", "Invalid email format")
    PROB_PASSWORD_CONSTRAINTS = ("password", "Password does not match constraints")


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
