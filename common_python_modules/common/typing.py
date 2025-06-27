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


class PermissionLevel(str, Enum):
    """Permission level enumeration used for user accounts."""

    USER = "user"
    ADMIN = "admin"


class HTTPErrorTypeDescription(tuple[int, str, str], Enum):
    """All error types (schemas) defined in OpenAPI doc.
    Included are statuscode, type and description.

    Error type and corresponding description for the problem IDs as determined in
    server/api/README.md."""

    PROB_USERNAME_EXISTS = (400, "username", "Username already in use")
    PROB_EMAIL_REGISTERED = (
        400,
        "email",
        "There already exists an account associated to this email",
    )
    PROB_USERNAME_CONSTRAINTS = (400, "username", "Username does not match constraints")
    PROB_INVALID_EMAIL = (400, "email", "Invalid email format")
    PROB_PASSWORD_CONSTRAINTS = (400, "password", "Password does not match constraints")

    ERROR_PASSWORD_VALIDATION_ERROR = (400, "password", "Password must be at least 6 characters \
                                       long")
    ERROR_INVALID_LOGIN = (400, "invalid", "Invalid username or password")

    PROB_INVALID_UUID = (401, "uuid", "User uuid does not match JWT")
    PROB_INVALID_KEY = (422, "key", "Given key is not an option")

    ERROR_NO_PROBLEMS_FOUND = (404, "not_found", "Problems not found")

    ERROR_USER_NOT_FOUND = (404, "user", "User not found")

    ERROR_PROBLEM_NOT_FOUND = (404, "problem", "Problem not found")

    ERROR_SUBMISSION_ENTRY_NOT_FOUND = (404, "submission", "Submission not found")
    ERROR_SUBMISSION_CODE_NOT_FOUND = (404, "submission", "Submission code not found")
    SUBMISSION_NOT_READY = (202, "wait", "Submission still processing")

    ERROR_REQUEST_FAILED = (400, "not_found", "Data for this problem not found")
    ERROR_NO_SCORES_FOUND = (400, "submissions", "No submissions found for this problem")

    ERROR_VALIDATION_FAILED = (
        400,
        "validation",
        "Title is required\nDifficulty must be one of: easy, medium, hard",
    )
    ERROR_INTERNAL_SERVER_ERROR = (500, "server_error", "An internal server error occurred")

    ERROR_INVALID_PERMISSION = (
        400,
        "Invalid permission level",
        "Permission level must be one of: user, admin"
    )
    ERROR_USERNAME_NOT_FOUND = (404, "not_found", "Username not found")

    ERROR_PROBLEM_VALIDATION_FAILED = (400, "validation", "problem_id must be a positive integer")

    ERROR_UNAUTHORIZED = (401, "unauthorized", "User does not have admin permissions")
    ERROR_TOKEN_EXPIRED = (401, "token_expired", "Token has expired")
    ERROR_TOKEN_INVALID = (401, "token_invalid", "Token is invalid")
    ERROR_USERNAME_VALIDATION_ERROR = (400, "username", "Username does not match constraints")
    ERROR_INVALID_USERNAME_OR_PASSWORD_COMBINATION = (
        400,
        "invalid",
        "Invalid username or password",
    )
    ERROR_OTHER_SERVER_ERROR = (400, "other", "An unexpected error occurred")
    ERROR_ENDPOINT_NOT_FOUND = (404, "not_found", "Endpoint not found")


class Difficulty(str, Enum):
    """
    Difficulty tags
    """
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    @classmethod
    def to_list(cls) -> list[str]:
        return [d.value for d in cls]
