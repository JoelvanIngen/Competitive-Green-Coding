from db.models.schemas import UserGet

from .jwt_handler import decode_access_token, create_access_token


def jwt_to_user(jwt_token: str) -> UserGet:
    """Converts JWT token to UserGet model"""

    return UserGet(**decode_access_token(jwt_token))


def user_to_jwt(user: UserGet) -> str:
    return create_access_token(user.model_dump())
