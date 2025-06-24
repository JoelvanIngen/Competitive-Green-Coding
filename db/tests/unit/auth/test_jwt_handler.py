from datetime import timedelta

import pytest
from jwt import ExpiredSignatureError, InvalidTokenError

from common.auth import create_access_token, decode_access_token
from common.schemas import PermissionLevel
from db import settings

# --- FIXTURES ---


@pytest.fixture(name="input_data")
def input_data_fixture():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "permission_level": PermissionLevel.USER,
        "avatar_id": 0,
    }


@pytest.fixture(name="instant_expiration_timedelta")
def instant_expiration_timedelta_fixture():
    return timedelta(minutes=0)


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)


def test_create_access_token_pass(input_data: dict):
    """Test if creation of access token is successful

    Args:
        input_data (dict): input data to be encoded into access token
    """
    create_access_token(
        input_data,
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM,
    )


def test_create_access_token_timedelta_pass(
    input_data: dict, instant_expiration_timedelta: timedelta
):
    """Test if creation of access token is successful if timedelta is given

    Args:
        input_data (dict): data to be encoded into access token
        instant_expiration_timedelta (timedelta): timedelta of 0 minutes
    """
    create_access_token(
        input_data, settings.JWT_SECRET_KEY, instant_expiration_timedelta, settings.JWT_ALGORITHM
    )


def test_decode_access_token_pass(input_data: dict):
    """Test if decode of access token is successful

    Args:
        input_data (dict): input data to be encoded into access token
    """
    token = create_access_token(
        input_data,
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM,
    )
    decode_access_token(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


def test_decode_access_token_expired_fail(
    input_data: dict, instant_expiration_timedelta: timedelta
):
    """Test if decode of expired access token raises ExpiredSignatureError

    Args:
        input_data (dict): input data to be encoded into access token
        instant_expiration_timedelta (timedelta): timedelta of 0 minutes
    """
    token = create_access_token(
        input_data, settings.JWT_SECRET_KEY, instant_expiration_timedelta, settings.JWT_ALGORITHM
    )

    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


def test_invalid_token_fail():
    """Test if decode of invalid token raises InvalidTokenError"""
    with pytest.raises(InvalidTokenError):
        decode_access_token("", settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_decode_token_result(input_data: dict):
    """Test if decode token results in input data

    Args:
        input_data (dict): input data to be encoded into access token
    """
    token = create_access_token(
        input_data,
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM,
    )
    output_data = decode_access_token(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

    assert isinstance(input_data, dict)
    assert isinstance(token, str)
    assert isinstance(output_data, dict)

    assert output_data["username"] == input_data["username"]
    assert output_data["email"] == input_data["email"]
    assert output_data["permission_level"] == input_data["permission_level"]
    assert output_data["avatar_id"] == input_data["avatar_id"]


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker
