"""
Implementation of OpenAPI docs, a gateway for all requests (from webserver).

Current routes:
*   /users/
*   /users/{name}

(/problems/, /submissions/ etc. to be added).

validates through Pydantic, then forwards to the DB microservice.
"""

from typing import Any, Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from common.schemas import (
    AddProblemRequest,
    AddProblemResponse,
    AdminProblemsResponse,
    LeaderboardRequest,
    LeaderboardResponse,
    LoginRequest,
    ProblemDetailsResponse,
    ProblemRequest,
    RegisterRequest,
    SubmissionRequest,
    SubmissionResponse,
    TokenResponse,
    UserGet,
    UserLogin,
    UserRegister,
)
from server.api import actions, proxy

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def _proxy_db_request(
    method: Literal["get", "post"],
    path_suffix: str,
    json_payload: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
):
    """
    Big boilerplate function to simplify all other functions
    :param method: HTTP method (get, post)
    :param path_suffix: specific API method to call in the DB handler
    :param json_payload: JSON payload (optional)
    :return: response from DB handler
    """

    async with httpx.AsyncClient() as client:
        try:
            url = f"{settings.DB_SERVICE_URL}/api{path_suffix}"
            if method == "get":
                if json_payload:
                    # Not allowed I think
                    raise NotImplementedError("Attempted to send json with GET request")

                resp = await client.get(url, timeout=settings.NETWORK_TIMEOUT, headers=headers)
            elif method == "post":
                resp = await client.post(
                    url, json=json_payload, timeout=settings.NETWORK_TIMEOUT, headers=headers
                )
            else:
                raise NotImplementedError(f"HTTP method {method} not implemented")

            if resp.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
                raise HTTPException(status_code=resp.status_code, detail=resp.json())

            return resp

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="could not connect to database service",
            ) from e

        except HTTPException as e:
            error_type, description = HTTPErrorTypeDescription[e.detail["detail"]]  # type: ignore

            if error_type:
                error_data = {"type": error_type, "description": description}
            else:
                error_data = {"type": "other", "description": "An unexpected error occured"}

            raise HTTPException(status_code=400, headers=error_data) from e

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while communicating with the database \
                    service: {e}",
            ) from e


@router.get(
    "/problem",
    response_model=ProblemGet,
    status_code=status.HTTP_200_OK,
)
async def get_problem_by_id(problem_request: ProblemRequest):
    return await actions.get_problem_by_id(problem_request)


@router.post(
    "/auth/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user: UserRegister):
    """
    1) Validate incoming JSON against UserRegister.
    2) Forward the payload to DB service's POST /auth/register.
    3) Relay the DB service's UserGet JSON back to the client.
    """
    return (
        await _proxy_db_request(
            "post",
            "/auth/register/",
            json_payload=user.model_dump(),
        )
    ).json()


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login_user(credentials: UserLogin):
    """
    1) Validate incoming JSON against UserLogin.
    2) Forward the payload to DB service's POST /auth/login.
    3) Relay the DB service's TokenResponse JSON back to the client.
    """
    return (
        await _proxy_db_request(
            "post",
            "/auth/login",
            json_payload=credentials.model_dump(),
        )
    ).json()


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
        await _proxy_db_request(
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


@router.get(
    "/problem",
    response_model=ProblemDetailsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get problem details",
    description=(
        "Retrieve detailed information about a specific programming problem "
        "for the submission page"
    ),
    responses={
        404: {
            "description": "Problem not found",
            "content": {
                "application/json": {"example": {"error": "No problem found with the given id"}}
            },
        }
    },
)
async def get_problem_details(problem_id: int = Query(...)):
    """
    Fetches full problem details by ID from the database service.

    This endpoint is called from the submission page and expects a 'problem_id'
    as a query parameter.
    Returns a 200 OK with problem data or 404 if the problem doesn't exist.
    """
    request = ProblemRequest(problem_id=problem_id)
    problem = await actions.get_problem_by_id(request)
    if problem is None:
        raise HTTPException(
            status_code=404, detail={"error": f"No problem found with id {problem_id}"}
        )
    return problem


# TODO: test if parameterpassing works
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
    1) Validate incoming JSON against LeaderboardRequest.
    2) Forward the payload to DB service's POST /auth/register.
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


# TODO: test if parameterpassing works
@router.post(
    "/admin/add-problem",
    response_model=AddProblemResponse,
    status_code=status.HTTP_200_OK,
)
async def add_problem(problem: AddProblemRequest, token: str = Depends(oauth2_scheme)):
    """
    1) Extract the JWT via OAuth2PasswordBearer.
    2) Forward a GET to DB service's /admin/add-problem with Authorization header.
    3) Relay the DB service's ProblemRequest JSON back to the client.
    """
    auth_header = {"Authorization": f"Bearer {token}"}
    return (
        await proxy.db_request(
            "post",
            "/admin/add-problem",
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


@router.get("/leaderboard}", response_model=LeaderboardGet)
async def read_leaderboard():
    """
    1) Forward GET /leaderboard to the DB service.
    2) If found, DB service returns leaderboard JSON {'entries': [list[LeaderboardEntryGet]]}.
    3) Relay that JSON back to the client.
    """
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{settings.DB_SERVICE_URL}/leaderboard", timeout=5.0)
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="could not connect to database service",
            ) from e

    if resp.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    return resp.json()
