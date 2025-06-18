"""
All proxy functions used by routers are defined here.
Security conciderations should be specified here

"""

from typing import Any, Literal

import httpx
from fastapi import HTTPException, status

from common.typing import HTTPErrorTypeDescription
from server.config import settings


async def db_request(
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
            try:
                status_code, error_type, description = HTTPErrorTypeDescription[
                    e.detail["detail"]  # type: ignore
                ]
            except KeyError:
                status_code, error_type, description = (400, "other", "An unexpected error occured")

            detail = {"type": error_type, "description": description}

            raise HTTPException(status_code=status_code, detail=detail) from e

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while communicating with the database \
                    service: {e}",
            ) from e
