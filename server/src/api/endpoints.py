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
import requests

from server.src.config import DB_SERVICE_URL
from server.src.models import UserResponse, UserRegister

router = APIRouter()


@router.post(
    "/users/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserRegister):
    """
    1) Validate incoming JSON against UserRegister.
    2) Forward the exact payload to the DB service’s POST /users/ endpoint.
    3) Relay the DB service’s JSON (which should match UserResponse) back to the client.
    """
    try:
        resp = requests.post(
            f"{DB_SERVICE_URL}/users/", json=user.dict(), timeout=5.0
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=503, detail="could not connect to database service"
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    return resp.json()


@router.get("/users/{username}", response_model=UserResponse)
def read_user(username: str):
    """
    1) Forward GET /users/{username} to the DB service.
    2) If found, DB service returns its user JSON (uuid, username, email).
    3) Relay that JSON back to the client.
    """
    try:
        resp = requests.get(f"{DB_SERVICE_URL}/users/{username}", timeout=5.0)
    except requests.RequestException:
        raise HTTPException(
            status_code=503, detail="could not connect to database service"
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    return resp.json()
