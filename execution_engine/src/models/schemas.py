from pydantic import BaseModel, Field
from typing import Literal


class ExecuteRequest(BaseModel):
    """
    Class that encapsulates all data necessary for execution of user's code

    This class is a bit boring and empty right now, but hopefully this will be useful in the future
    """

    code: str = Field(..., description="The submitted code from the user")


class ExecuteResult(BaseModel):
    """
    Class that encapsulates all results from execution
    """

    runtime_ms: int = 0,
    mem_usage_mb: int = 0,
    status: Literal[
        "success",  # Yay
        "failed",  # Tests failed
        "mem_limit_exceeded",  # Used too much memory
        "timeout",  # Ran out of time and was terminated
        "security_violation",  # In case we decide to implement keyword checking to prevent scary keywords
        "compile_error",  # Couldn't compile user's code
        "runtime_error",  # User's code failed (segfaults, etc)
        "internal_error",  # Blanket error for everything unexpected (not user's fault)
    ] = "internal_error",
    error_msg: str = "",  # Error that we want to show the user (such as compiler/stderr output)
