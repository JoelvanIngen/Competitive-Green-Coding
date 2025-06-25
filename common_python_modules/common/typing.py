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

    ### Login page [Jona] ###
    # /api/auth/register
    PROB_USERNAME_EXISTS = (400, "username", "Username already in use")
    PROB_EMAIL_REGISTERED = (
        400,
        "email",
        "There already exists an account associated to this email",
    )
    PROB_USERNAME_CONSTRAINTS = (400, "username", "Username does not match constraints")
    PROB_INVALID_EMAIL = (400, "email", "Invalid email format")
    PROB_PASSWORD_CONSTRAINTS = (400, "password", "Password does not match constraints")

    # /api/auth/login
    # ERROR_INVALID_USERNAME_OR_PASSWORD_COMBINATION
    # ERROR_USERNAME_VALIDATION_ERROR

    ERROR_PASSWORD_VALIDATION_ERROR = (400, "password", "Password must be at least 6 characters long")
    Unauthorized = (400, "invalid", "Invalid username or password")

    ### Problems page [Abe] ###
    # GET /api/problems
    ERROR_NO_PROBLEMS_FOUND = (404, "not_found", "Problems not found")

    # POST /api/problems
    # ERROR_INVALID_USERNAME_OR_PASSWORD_COMBINATION

    ### Discussion board page [Abe] ###
    # GET /api/discussion

    # POST /api/discussion

    ### Thread detail page [Abe] ###
    # /api/discussion/{thread-id}
    ERROR_THREAD_NOT_FOUND = (404, "not_found", "Thread not found")

    # GET /api/discussion/{thread-id}/comments

    # POST /api/discussion/{thread-id}/comments

    ### Profile page [Abe] ###
    # GET /api/profile/{username}
    ERROR_USER_NOT_FOUND = (404, "not_found", "User not found")``

    # POST /api/profile/{username}

    ### Submission page [Martijn]
    # /api/problem
    ERROR_PROBLEM_NOT_FOUND = (404, "not_found", "Problem not found")

    # /api/submission
    # ERROR_PROBLEM_NOT_FOUND = (404, "not_found", "Problem not found")

    ### Leaderboard page [Adib] ###
    # /api/leaderboard
    ERROR_REQUEST_FAILED = (400, "not_found", "Data for this problem not found")

    ### Admin page [Adam] ###
    # /api/admin/my-problems
    # ERROR_ENDPOINT_NOT_FOUND = (404, "not_found", "Endpoint not found")

    # /api/admin/add-problem
    ERROR_VALIDATION_FAILED = (
        400,
        "validation",
        "Title is required\nDifficulty must be one of: easy, medium, hard",
    )
    ERROR_INTERNAL_SERVER_ERROR = (500, "server_error", "An internal server error occurred")


    # /api/admin/change-permission
    ERROR_INVALID_PERMISSION = (
        400,
        "Invalid permission level",
        "Permission level must be one of: user, admin"
    )
    ERROR_USER_NOT_FOUND = (404, "user_not_found", "Could not find user with that username")

    ### Universly used errors ###

    ERROR_UNAUTHORIZED = (401, "unauthorized", "User does not have admin permissions")
    ERROR_USERNAME_VALIDATION_ERROR = (400, "username", "Username does not match constraints")
    ERROR_INVALID_USERNAME_OR_PASSWORD_COMBINATION = (
        400,
        "invalid",
        "Invalid username or password",
    )
    ERROR_OTHER_SERVER_ERROR = (400, "other", "An unexpected error occurred")
    ERROR_ENDPOINT_NOT_FOUND = (404, "not_found", "Endpoint not found")


    # ERROR_DATE = (444, "date", "date is not very good")
    # ERROR_INV = (445, "inv", "invalid")
    # ERROR_PERM = (446, "perm", "permission denied")


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
