from enum import Enum


class ErrorReason(str, Enum):
    """Every reason code execution can fail"""

    TESTS_FAILED = "tests_failed"  # Tests failed
    MEM_LIMIT = "mem_limit"  # Used too much memory
    TIMEOUT = "timeout"
    SECURITY = "security"  # Ran out of time and was terminated
    # In case we decide to implement keyword checking to prevent scary keywords
    COMPILE_ERROR = "compile_error"  # Couldn't compile user's code
    RUNTIME_ERROR = "runtime_error"  # User's code failed (segfaults, etc)
    INTERNAL_ERROR = "internal_error"  # Blanket error for everything unexpected (not user's fault)


class Language(str, Enum):
    """Available languages"""

    C = "c"
    PYTHON = "python"


class PermissionLevel(str, Enum):
    """Permission level enumeration used for user accounts."""

    USER = "user"
    ADMIN = "admin"


class ErrorType(str, Enum):
    """All error types (schemas) defined in OpenAPI doc."""

    ERROR_RESPONSE = "ErrorResponse"
    REGISTER_ERROR_RESPONSE = "RegisterErrorResponse"
    LEADERBOARD_ERROR_RESPONSE = "LeaderboardErrorResponse"
    PROBLEM_ERROR_RESPONSE = "ProblemErrorResponse"
    SUBMISSION_ERROR_RESPONSE = "SubmissionErrorResponse"
    ADMIN_ERROR_RESPONSE = "AdminErrorResponse"
    ADMIN_DETAILED_ERROR_RESPONSE = "AdminDetailedErrorResponse"


class HTTPErrorTypeDescription(tuple[str, str], Enum):
    """Error type and corresponding description for the problem IDs as determined in
    server/api/README.md."""

    PROB_USERNAME_EXISTS = ("username", "Username already in use")
    PROB_EMAIL_REGISTERED = ("email", "There already exists an account associated to this email")
    PROB_USERNAME_CONSTRAINTS = ("username", "Username does not match constraints")
    PROB_INVALID_EMAIL = ("email", "Invalid email format")
    PROB_PASSWORD_CONSTRAINTS = ("password", "Password does not match constraints")
