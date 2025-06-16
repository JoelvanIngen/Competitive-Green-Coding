"""
#TODO:
- move from Depends to Security
- CORS middleware
- Rate limiting
- Update schemas
- Docs
- (add token check here?)


endpoints.py

gateway for public requests (from webserver).

Necessary routes are documented in documentation/de_interface.yaml

validates through Pydantic, then forwards to the DB microservice.
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer

from server.src.server.api import actions
from server.src.server.api import proxy
from server.config import settings
from server.models import UserGet
from server.models.schemas import (
    TokenResponse,
    ProblemRequest, ProblemDetailsResponse,
    LeaderboardRequest, LeaderboardResponse,
    LoginRequest, RegisterRequest,
    SubmissionRequest, SubmissionResponse,
    AdminProblemsResponse, AddProblemRequest
)


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ============================================================================
# Login page Endpoints [Jona]
# ============================================================================
# Public endpoints: No authentication required for these endpoints.

@router.post(
    "/auth/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login_user(credentials: LoginRequest):
    """
    1) Validate incoming JSON against LoginRequest.
    2) Forward the payload to DB service's POST /auth/login.
    3) Relay the DB service's TokenResponse JSON back to the client.
    """
    return (
        await proxy.db_request(
            "post",
            "/auth/login",
            json_payload=credentials.model_dump(),
        )
    ).json()


@router.post(
    "/auth/register",
    response_model=UserGet,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user: RegisterRequest):
    """
    1) Validate incoming JSON against RegisterRequest.
    2) Forward the payload to DB service's POST /auth/register.
    3) Relay the DB service's UserGet JSON back to the client.
    """
    return (
        await proxy.db_request(
            "post",
            "/auth/register",
            json_payload=user.model_dump(),
        )
    ).json()

# ============================================================================
# User page Endpoints
# ============================================================================
# Authenticated endpoints: Requires valid JWT token in Authorization header.

@router.get(
    "/users/me",
    response_model=UserGet,
    status_code=status.HTTP_200_OK,
)
async def read_current_user(token: str = Depends(oauth2_scheme)):
    """
    1) Extract the JWT via OAuth2PasswordBearer.
    2) Forward a GET to DB service's /users/me with Authorization header.
    3) Relay the DB service's UserGet JSON back to the client.
    """
    auth_header = {"Authorization": f"Bearer {token}"}
    return (
        await proxy.db_request(
            "get",
            "/users/me",
            headers=auth_header,
        )
    ).json()

# ============================================================================
# Problems page Endpoints [Abe]
# ============================================================================
# Public endpoints: No authentication required.


# ============================================================================
# Submission page Endpoints [Martijn]
# ============================================================================
# Authenticated endpoints: Requires valid JWT token in Authorization header.

# TODO: problem_id gets sent as query parameter, is this function catching it?
@router.get(
    "/problem",
    response_model=ProblemDetailsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_problem_by_id(problem_request: ProblemRequest):
    return (
        await proxy.db_request(
            "get",
            "/problem",
            json_payload=problem_request.model_dump(),
        )
    ).json()


# TODO: header and body in parameters; does this work?
@router.post(
    "/submission",
    response_model=SubmissionResponse,
    status_code=status.HTTP_200_OK,
)
async def post_submission(submission: SubmissionRequest, token: str = Depends(oauth2_scheme)):
    """
    1) Extract the JWT via OAuth2PasswordBearer.
    2) Forward a POST to DB service's /submission with Authorization header.
    3) Relay the DB service's SubmissionResponse JSON back to the client.
    """
    auth_header = {"Authorization": f"Bearer {token}"}
    return (
        await proxy.db_request(
            "post",
            "/submission",
            headers=auth_header,
            json_payload=submission.model_dump(),
        )
    ).json()

# ============================================================================
# Leaderboard page Endpoints [Adib]
# ============================================================================
# Public endpoints: No authentication required.

@router.post(
        "/leaderboard",
        response_model=LeaderboardResponse,
        status_code=status.HTTP_200_OK,
)
async def read_leaderboard(leaderboard_request: LeaderboardRequest):
    """
    1) Forward GET /leaderboard to the DB service.
    2) If found, DB service returns leaderboard JSON:
       {'entries': [list[LeaderboardEntryGet]]}.
    3) Relay that JSON back to the client.
    """
    return (
        await proxy.db_request(
            "post",
            "/leaderboard",
            json_payload=leaderboard_request.model_dump(),
        )
    ).json()

# ============================================================================
# Admin page Endpoints [Adam]
# ============================================================================
# Authenticated endpoints: Requires valid JWT token in Authorization header.

@router.get(
    "/admin/my-problems",
    response_model=AdminProblemsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_admin_problems(token: str = Depends(oauth2_scheme)):
    """
    1) Extract the JWT via OAuth2PasswordBearer.
    2) Forward a GET to DB service's /admin/my-problems with Authorization header.
    3) Relay the DB service's AdminProblemsResponse JSON back to the client.
    """
    auth_header = {"Authorization": f"Bearer {token}"}
    return (
        await proxy.db_request(
            "get",
            "/admin/my-problems",
            headers=auth_header,
        )
    ).json()


# TODO: header and body in parameters; does this work?
@router.post(
    "/admin/add-problem",
    response_model=ProblemRequest,
    status_code=status.HTTP_200_OK,
)
async def get_admin_problems(problem: AddProblemRequest, token: str = Depends(oauth2_scheme)):
    """
    1) Extract the JWT via OAuth2PasswordBearer.
    2) Forward a GET to DB service's /admin/add-problem with Authorization header.
    3) Relay the DB service's ProblemRequest JSON back to the client.
    """
    auth_header = {"Authorization": f"Bearer {token}"}
    return (
        await proxy.db_request(
            "get",
            "/admin/my-problems",
            headers=auth_header,
            json_payload=problem.model_dump(),
        )
    ).json()

# ============================================================================
# Health Check Endpoints
# ============================================================================
# Public endpoints: No authentication required for these endpoints.

@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "message": "DB service is running"}