from datetime import timedelta
from uuid import uuid4

import pytest
from jwt import InvalidTokenError

from common.auth import data_to_jwt, jwt_to_data
from common.schemas import JWTokenData, PermissionLevel
from db import settings

# --- FIXTURES ---


@pytest.fixture(name="jwtokendata_data")
def jwtokendata_data_fixture():
    return {
        "uuid": str(uuid4()),
        "username": "testuser",
        "permission_level": PermissionLevel.USER,
        "avatar_id": 0,
    }


@pytest.fixture(name="jwtokendata")
def jwtokendata_fixture(jwtokendata_data):
    return JWTokenData(**jwtokendata_data)


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)


def test_data_to_jwt_pass(jwtokendata: JWTokenData):
    """Check if creation of access token is successful

    Args:
        jwtokendata (JWTokenData): data to include in token
    """
    data_to_jwt(
        jwtokendata,
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM
    )


def test_user_to_jwt_to_user_pass(jwtokendata: JWTokenData):
    """Check if decode of created access token is successful

    Args:
        jwtokendata (JWTokenData): data to include in token
    """
    token = data_to_jwt(
        jwtokendata,
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM
    )
    jwt_to_data(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


def test_invalid_token_fail():
    """Test if decode of invalid token raises InvalidTokenError
    """
    with pytest.raises(InvalidTokenError):
        jwt_to_data(
            "",
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM
        )


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_data_to_jwt_result(jwtokendata: JWTokenData):
    """Check if result of decode of generated access token is the same as the input

    Args:
        jwtokendata (JWTokenData): data to include in token
    """
    token = data_to_jwt(
        jwtokendata,
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM
    )
    output_jwtokendata = jwt_to_data(
        token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    )

    assert isinstance(jwtokendata, JWTokenData)
    assert isinstance(output_jwtokendata, JWTokenData)
    assert jwtokendata == output_jwtokendata


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker
