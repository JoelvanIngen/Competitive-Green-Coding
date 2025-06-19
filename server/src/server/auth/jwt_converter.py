from common.schemas import JWTokenData

from .jwt_handler import create_access_token, decode_access_token


def jwt_to_data(jwt_token: str) -> JWTokenData:
    """Converts JWT token to JWTokenData model"""

    return JWTokenData(**decode_access_token(jwt_token))


def data_to_jwt(user: JWTokenData) -> str:
    return create_access_token(user.model_dump())
