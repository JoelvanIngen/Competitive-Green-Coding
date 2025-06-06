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
from fastapi import APIRouter, HTTPException, status

from server.config import DB_SERVICE_URL, DB_SERVICE_TIMEOUT_SEC
from server.models import UserGet, UserPost

router = APIRouter()


async def _proxy_db_request(
        method: Literal["get", "post"],
        path_suffix: str,
        json_payload: dict[str, Any] | None = None,
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

                resp = await client.get(url, timeout=DB_SERVICE_TIMEOUT_SEC)
            elif method == "post":
                resp = await client.post(url, json=json_payload, timeout=DB_SERVICE_TIMEOUT_SEC)
            else:
                raise NotImplementedError(f"HTTP method {method} not implemented")

            if resp.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
                raise HTTPException(status_code=resp.status_code, detail=resp.json())

            return resp

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="could not connect to database service",
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while communicating with the database service: {e}",
            )


@router.post(
    "/users/",
    response_model=UserPost,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserPost):
    """
    1) Validate incoming JSON against UserRegister.
    2) Forward the exact payload to the DB service’s POST /users/ endpoint.
    3) Relay the DB service’s JSON (which should match UserResponse) back to
        the client.
    """

    return (await _proxy_db_request(
        "post",
        "/users/",
        json_payload=user.model_dump(),
    )).json()


@router.get("/users/{username}", response_model=UserGet)
async def read_user(username: str):
    """
    1) Forward GET /users/{username} to the DB service.
    2) If found, DB service returns its user JSON (uuid, username, email).
    3) Relay that JSON back to the client.
    """

    return (await _proxy_db_request(
        "get",
        f"/users/{username}",
    )).json()


@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "message": "DB service is running"}
