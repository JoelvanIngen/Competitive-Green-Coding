"""
Direct entrypoint for endpoints.py.
- This module should not see DB models.
"""

from http.client import HTTPException

import jwt
from loguru import logger
from sqlmodel import Session

from db.api.modules.bitmap_translator import translate_tags_to_bitmap
from db.auth import jwt_to_user, user_to_jwt
from db.engine.queries import try_get_user_by_username
from db.models.convert import db_user_to_user
from db.models.db_schemas import ProblemEntry
from db.models.schemas import TokenResponse, UserGet, UserLogin, LeaderboardGet, ProblemPost



def login_user(s: Session, login: UserLogin) -> TokenResponse:
    """
    Logs in a user and returns a TokenResponse.
    :raises HTTPException 401: On invalid credentials.
    """

    # TODO: We should very probably check for password too

    user_entry = try_get_user_by_username(s, login.username)
    if not user_entry:
        raise HTTPException(401, "Unauthorized")

    user = db_user_to_user(user_entry)
    jwt_token = user_to_jwt(user)
    return TokenResponse(access_token=jwt_token)


def lookup_current_user(token: TokenResponse) -> UserGet:
    """
    Looks up the current user
    :raises HTTPException 401: On expired token or on invalid token
    :raises HTTPException 500: On unexpected error
    """

    try:
        return jwt_to_user(token.access_token)
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(401, "Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(401, "Unauthorized") from e
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error") from e


def lookup_user(s: Session, username: str) -> UserGet:
    user_entry = try_get_user_by_username(s, username)
    if not user_entry:
        raise HTTPException(404, "User not found")

    return db_user_to_user(user_entry)
