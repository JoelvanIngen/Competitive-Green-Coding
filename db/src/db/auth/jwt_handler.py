from datetime import datetime, timedelta, timezone

import jwt

SECRET_KEY = "838066cf2248ce8ec4ee78a9707c365b73da33d56241b55a65c98b3ddf09020f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def encode_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodes JWT token
    :raises jwt.ExpiredSignatureError: On expired token
    :raises jwt.InvalidTokenError: On invalid token
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
