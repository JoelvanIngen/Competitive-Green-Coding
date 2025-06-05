from typing import Literal

from pydantic import BaseModel, Field

status_t = Literal[
    "success",  # Yay
    "failed",  # Tests failed
    "mem_limit_exceeded",  # Used too much memory
    "timeout",  # Ran out of time and was terminated
    "security_violation",  # In case we decide to implement keyword checking
                           # to prevent scary keywords
    "compile_error",  # Couldn't compile user's code
    "runtime_error",  # User's code failed (segfaults, etc)
    "internal_error",  # Blanket error for everything unexpected
                       # (not user's fault)
]


class ExecuteRequest(BaseModel):
    """
    Class that encapsulates all data necessary for execution of user's code
    This class is a bit boring and empty right now, but hopefully this will
    be useful in the future
    Current proposed path for solution file:
        /storage/{user_uuid}/{problem_uuid}/latest.c
    """
    user_uuid: str = Field(
        ...,
        description="UUID of the user who submitted the solution")
    problem_uuid: str = Field(..., description="UUID of the problem")


class ExecuteResult(BaseModel):
    """
    Class that encapsulates all results from execution
    """
    runtime_ms: int = Field(..., description="Runtime in milliseconds")
    mem_usage_mb: int = Field(..., description="Memory usage in MB")
    status: status_t = Field(
        ...,
        description="Execution status (success or reason for failure)")
    error_msg: str = Field(..., description="Error message to show the user")
