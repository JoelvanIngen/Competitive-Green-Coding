"""
Implementation of OpenAPI docs, a gateway for all requests (from webserver).

Current routes:
*   /users/
*   /users/{name}

(/problems/, /submissions/ etc. to be added).

validates through Pydantic, then forwards to the DB microservice.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer

from common.schemas import (
    AddProblemRequest,
    ChangePermissionRequest,
    LeaderboardRequest,
    LeaderboardResponse,
    LoginRequest,
    ProblemAllRequest,
    ProblemDetailsResponse,
    ProblemRequest,
    ProblemsListResponse,
    RegisterRequest,
    RemoveProblemRequest,
    RemoveProblemResponse,
    SettingUpdateRequest,
    SubmissionIdentifier,
    SubmissionRequest,
    SubmissionResult,
    TokenResponse,
    UserGet,
    UserProfileResponse,
)
from server.api import actions, proxy

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
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user: RegisterRequest):
    """
    1) Validate incoming JSON against RegisterRequest.
    2) Forward the payload to DB service's POST /auth/register.
    3) Relay the DB service's TokenResponse JSON back to the client.
    """
    return (
        await proxy.db_request(
            "post",
            "/auth/register",
            json_payload=user.model_dump(),
        )
    ).json()


@router.put(
    "/settings",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user(user: SettingUpdateRequest, token: str = Depends(oauth2_scheme)):
    """
    1) Validate incoming JSON against SettingUpdateRequest.
    2) Forward the payload to DB service's POST /settings.
    3) Relay the DB service's TokenResponse JSON back to the client.
    """

    auth_header = {"Authorization": f"Bearer {token}"}
    return (
        await proxy.db_request(
            "put",
            "/settings",
            json_payload=user.model_dump(),
            headers=auth_header,
        )
    ).json()


# ============================================================================
# Profile page Endpoints
# ============================================================================
# Authenticated endpoints: Requires valid JWT token in Authorization header.


@router.get(
    "/settings",
    response_model=UserGet,
    status_code=status.HTTP_200_OK,
)
async def get_user_information(token: str = Depends(oauth2_scheme)):
    """
    1) Extract the JWT out the header.
    2) Forward a GET to DB service's /settings with Authorization header.
    3) Relay the DB service's UserGet JSON back to the client.
    """
    auth_header = {"Authorization": f"Bearer {token}"}
    return (
        await proxy.db_request(
            "get",
            "/settings",
            headers=auth_header,
        )
    ).json()


@router.get(
    "/profile/{username}",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def get_profile_from_username(username: str) -> UserProfileResponse:
    return (
        await proxy.db_request(
            "get",
            f"/profile/{username}",
        )
    ).json()


# ============================================================================
# Problems page Endpoints [Abe]
# ============================================================================
# Public endpoints: No authentication required.


@router.post(
    "/problems/all",
    response_model=ProblemsListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_all_problems(request: ProblemAllRequest):
    """
    Fetches all problems (basic info), up to an optional limit.
    """
    return (
        await proxy.db_request(
            "post",
            "/problems/all",
            json_payload=request.model_dump(),
        )
    ).json()


# ============================================================================
# Submission page Endpoints [Martijn]
# ============================================================================
# Authenticated endpoints: Requires valid JWT token in Authorization header.


@router.get(
    "/problem",
    response_model=ProblemDetailsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_problem_details(problem_id: int = Query(...), token: str = Depends(oauth2_scheme)):
    """
    Fetches full problem details by ID from the database service.

    This endpoint is called from the submission page and expects a 'problem_id'
    as a query parameter.
    Returns a 200 OK with problem data or 404 if the problem doesn't exist.
    """
    request = ProblemRequest(problem_id=problem_id)
    auth_header = {"authorization": token}

    problem = await actions.get_problem_by_id(request, auth_header)
    if problem is None:
        raise HTTPException(
            status_code=404, detail={"error": f"No problem found with id {problem_id}"}
        )
    return problem


# TODO: test if parameterpassing works
@router.post(
    "/submission",
    response_model=SubmissionIdentifier,
    status_code=status.HTTP_201_CREATED,
)
async def post_submission(submission: SubmissionRequest, token: str = Depends(oauth2_scheme)):
    """
    1) Extract the JWT via OAuth2PasswordBearer.
    2) Forward a POST to DB service's /submission with Authorization header.
    3) Relay the DB service's SubmissionResponse JSON back to the client.
    """
    auth_header = {"Authorization": f"Bearer {token}"}
    return await actions.post_submission(submission, auth_header, token)


@router.post(
    "/submission-result",
    response_model=SubmissionResult,
    status_code=status.HTTP_200_OK,
)  # rename submission schema below ? most appropriate for this use case but inappropriate name
async def get_submission(submission: SubmissionIdentifier, token: str = Depends(oauth2_scheme)):
    """
    1) Extract the JWT via OAuth2PasswordBearer.
    2) Forward a POST to DB service's /submission-get with Authorization header.
    3) Relay the DB service's SubmissionResult JSON back to the client.
    """
    auth_header = {"Authorization": f"Bearer {token}"}
    return await actions.get_submission_result(submission, auth_header)


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
    1) Validate incoming JSON against LeaderboardRequest.
    2) Forward the payload to DB service's POST /leaderboard.
    3) Relay the DB service's LeaderboardResponse JSON back to the client.
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


# TODO: test if parameterpassing works


@router.post(
    "/admin/add-problem",
    response_model=ProblemDetailsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_problem(problem: AddProblemRequest, token: str = Depends(oauth2_scheme)):
    """
    1) Extract the JWT via OAuth2PasswordBearer.
    2) Forward a POST to DB service's /admin/add-problem with Authorization header.
    3) Relay the DB service's ProblemDetailsResponse JSON back to the client.
    """

    auth_header = {"Authorization": f"Bearer {token}"}
    return (
        await proxy.db_request(
            "post",
            "/admin/add-problem",
            json_payload=problem.model_dump(),
            headers=auth_header,
        )
    ).json()


@router.post(
    "/admin/change-permission",
    response_model=UserGet,
    status_code=status.HTTP_200_OK,
)
async def change_user_permission(request: ChangePermissionRequest, token: str = Depends(oauth2_scheme)):
    """
    1) Extract the JWT via OAuth2PasswordBearer.
    2) Forward a POST to DB service's /admin/change-permission with Authorization header.
    3) Relay the DB service's UserGet JSON back to the client.
    """

    auth_header = {"Authorization": f"Bearer {token}"}
    return (
        await proxy.db_request(
            "post",
            "/admin/change-permission",
            json_payload=request.model_dump(),
            headers=auth_header,
        )
    ).json()


@router.post(
    "/admin/remove-problem",
    response_model=RemoveProblemResponse,
    status_code=status.HTTP_200_OK,
    tags=["Admin page"],
)
async def remove_problem(
    request: RemoveProblemRequest,
    token: str = Depends(oauth2_scheme),
):
    """
    Delete an existing problem (admin only).
    """
    auth_header = {"Authorization": f"Bearer {token}"}
    return (
        await proxy.db_request(
            "post",
            "/admin/remove-problem",
            json_payload=request.model_dump(),
            headers=auth_header,
        )
    ).json()


# ============================================================================
# Health Check Endpoints
# ============================================================================
# Public endpoints: No authentication required for these endpoints.


@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "message": "DB service is running"}
