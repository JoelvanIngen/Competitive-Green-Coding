from pydantic import BaseModel, Field

from execution_engine.typing import LanguageLiteral, StatusType


class ExecuteRequest(BaseModel):
    """
    Class that encapsulates all data necessary for execution of user's code
    This class is a bit boring and empty right now, but hopefully this will
    be useful in the future
    Current proposed path for solution file:
        /storage/{user_uuid}/{problem_uuid}/latest.c
    """

    user_uuid: str = Field(..., description="UUID of the user who submitted the solution")
    problem_uuid: str = Field(..., description="UUID of the problem")
    language: LanguageLiteral = Field(..., description="Language being used")
    code: str = Field(..., description="Code submitted by the user")


class ExecuteResult(BaseModel):
    """
    Class that encapsulates all results from execution
    """

    runtime_ms: int = Field(..., description="Runtime in milliseconds")
    mem_usage_mb: int = Field(..., description="Memory usage in MB")
    status: StatusType = Field(..., description="Execution status (success or reason for failure)")
    error_msg: str = Field(..., description="Error message to show the user")
