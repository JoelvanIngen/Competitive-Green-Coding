from enum import Enum

from pydantic import BaseModel, Field


class HTTPErrorTypeDescription(tuple[str, str], Enum):
    """Permission level enumeration used for user accounts."""

    PROB_USERNAME_EXISTS = ("username", "Username already in use")
    PROB_EMAIL_REGISTERED = ("email", "There already exists an account associated to this email")
    PROB_USERNAME_CONSTRAINTS = ("username", "Username does not match constraints")
    PROB_INVALID_EMAIL = ("email", "Invalid email format")
    PROB_PASSWORD_CONSTRAINTS = ("password", "Password does not match constraints")


class ProblemRequest(BaseModel):
    """Schema to communicate request for a problem by problem-id."""

    problem_id: int = Field()
