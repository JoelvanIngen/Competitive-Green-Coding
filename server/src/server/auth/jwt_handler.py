"""
jwt_handler.py

Contains functions to create and decode JSON Web Tokens.
Used by db handler to hand out and decode user credential tokens after logging in.
"""

from datetime import datetime, timedelta, timezone

import jwt

from db import settings


def create_access_token(
    data: dict, expires_delta: timedelta = timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
) -> str:
    """Create JSON Web access Token carrying data and expiring after expires_delta.

    Args:
        data (dict): data to be encoded into the JWT
        expires_delta (timedelta, optional): amount of time the JWT is valid.
            Defaults to timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).

    Returns:
        str: encoded JSON Web Token
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Retrieve payload data by decoding input token.

    Args:
        token (str): input JSON Web Token

    Raises:
        jwt.ExpiredSignatureError: On expired token
        jwt.InvalidTokenError: On invalid token

    Returns:
        dict: payload data of JSON Web Token
    """

    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
