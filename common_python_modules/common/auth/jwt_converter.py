from common.schemas import JWTokenData
from datetime import timedelta

from .jwt_handler import create_access_token, decode_access_token


def jwt_to_data(jwt_token: str, key: str, algorithm: str) -> JWTokenData:
    """Converts JWT token to JWTokenData model"""

    return JWTokenData(**decode_access_token(jwt_token, key, algorithm))


def data_to_jwt(user: JWTokenData, key: str, expires_delta: timedelta, algorithm: str) -> str:
    return create_access_token(user.model_dump(), key, expires_delta, algorithm)
