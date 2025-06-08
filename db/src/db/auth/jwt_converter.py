from db.auth import encode_access_token
from db.auth.jwt_handler import decode_access_token
from db.models.schemas import UserGet


def jwt_to_user(jwt_token: str) -> UserGet:
    """Converts JWT token to UserGet model"""

    return UserGet(**decode_access_token(jwt_token))


def user_to_jwt(user: UserGet) -> str:
    return encode_access_token(user.model_dump())
