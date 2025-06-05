"""
endpoints.py

gateway for public requests (from webserver).

Current routes:
*   /users/
*   /users/{name}

(/problems/, /submissions/ etc. to be added).

validates through Pydantic, then forwards to the DB microservice.
"""

from fastapi import APIRouter, HTTPException, status
import httpx

from ..config import DB_SERVICE_URL
from ..models import UserGet, UserPost

router = APIRouter()


@router.post(
    "/users/",
    response_model=UserPost,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserPost):
    """
    1) Validate incoming JSON against UserRegister.
    2) Forward the exact payload to the DB service’s POST /users/ endpoint.
    3) Relay the DB service’s JSON (which should match UserResponse) back to the client.
    """
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{DB_SERVICE_URL}/users/", json=user.model_dump(), timeout=5.0
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="could not connect to database service",
            )

    if resp.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    return resp.json()


@router.get("/users/{username}", response_model=UserGet)
async def read_user(username: str):
    """
    1) Forward GET /users/{username} to the DB service.
    2) If found, DB service returns its user JSON (uuid, username, email).
    3) Relay that JSON back to the client.
    """
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{DB_SERVICE_URL}/users/{username}", timeout=5.0
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="could not connect to database service",
            )

    if resp.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    return resp.json()
