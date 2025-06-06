"""
endpoints.py

gateway for public requests (from webserver).

Current routes:
*   /users/
*   /users/{name}

(/problems/, /submissions/ etc. to be added).

validates through Pydantic, then forwards to the DB microservice.
"""

from typing import Any, Literal

import httpx
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from server.config import DB_SERVICE_URL, DB_SERVICE_TIMEOUT_SEC
from server.models import UserGet
from server.models.schemas import UserRegister, UserLogin, TokenResponse

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
            url = f"{DB_SERVICE_URL}{path_suffix}"
            if method == "get":
                if json_payload:
                    # Not allowed I think
                    raise NotImplementedError("Attempted to send json with GET request")

                resp = await client.get(url, timeout=DB_SERVICE_TIMEOUT_SEC, headers=headers)
            elif method == "post":
                resp = await client.post(url, json=json_payload, timeout=DB_SERVICE_TIMEOUT_SEC,
                                         headers=headers)
            else:
                raise NotImplementedError(f"HTTP method {method} not implemented")

            if resp.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
                raise HTTPException(status_code=resp.status_code, detail=resp.json())

            return resp

        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="could not connect to database service",
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while communicating with the database \
                    service: {e}",
            )


@router.post(
    "/auth/register",
    response_model=UserGet,
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
            "/auth/register",
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
