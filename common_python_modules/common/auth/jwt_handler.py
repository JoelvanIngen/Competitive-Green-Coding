"""
jwt_handler.py

Contains functions to create and decode JSON Web Tokens.
Used by db handler to hand out and decode user credential tokens after logging in.
"""

from datetime import datetime, timedelta, timezone

import jwt


def create_access_token(data: dict, key: str, expires_delta: timedelta, algorithm: str) -> str:
    """Create JSON Web access Token carrying data and expiring after expires_delta.

    Args:
        data (dict): data to encode in the JWT
        key (str): secret key to encode the JWT with
        expires_delta (timedelta): lifetime of the JWT
        algorithm (str): algorithm used for encoding

    Returns:
        str: JWT token response
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key, algorithm=algorithm)

    return encoded_jwt


def decode_access_token(token: str, key: str, algorithm: str) -> dict:
    """Retrieve payload data by decoding input token.

    Args:
        token (str): input JSON Web Token
        key (str): secret key to encode the JWT with
        algorithm (str): algorithm used for encoding

    Raises:
        jwt.ExpiredSignatureError: On expired token
        jwt.InvalidTokenError: On invalid token

    Returns:
        dict: payload data of JSON Web Token
    """

    return jwt.decode(token, key, algorithms=[algorithm])
