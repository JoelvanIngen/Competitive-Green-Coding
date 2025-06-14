import datetime

import pytest
from jwt import ExpiredSignatureError, InvalidTokenError

from db.auth.jwt_handler import create_access_token, decode_access_token
from common.schemas import PermissionLevel

# --- FIXTURES ---


@pytest.fixture(name="input_data")
def input_data_fixture():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "permission_level": PermissionLevel.USER
    }


@pytest.fixture(name="instant_expiration_timedelta")
def instant_expiration_timedelta_fixture():
    return datetime.timedelta(minutes=0)


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
    create_access_token(input_data)


def test_create_access_token_timedelta_pass(
    input_data: dict,
    instant_expiration_timedelta: datetime.timedelta
):
    """Test if creation of access token is successful if timedelta is given

    Args:
        input_data (dict): data to be encoded into access token
        instant_expiration_timedelta (datetime.timedelta): timedelta of 0 minutes
    """
    create_access_token(input_data, instant_expiration_timedelta)


def test_decode_access_token_pass(input_data: dict):
    """Test if decode of access token is successful

    Args:
        input_data (dict): input data to be encoded into access token
    """
    token = create_access_token(input_data)
    decode_access_token(token)


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


def test_decode_access_token_expired_fail(
    input_data: dict,
    instant_expiration_timedelta: datetime.timedelta
):
    """Test if decode of expired access token raises ExpiredSignatureError

    Args:
        input_data (dict): input data to be encoded into access token
        instant_expiration_timedelta (datetime.timedelta): timedelta of 0 minutes
    """
    token = create_access_token(input_data, instant_expiration_timedelta)

    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token)


def test_invalid_token_fail():
    """Test if decode of invalid token raises InvalidTokenError
    """
    with pytest.raises(InvalidTokenError):
        decode_access_token("")


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_decode_token_result(input_data: dict):
    """Test if decode token results in input data

    Args:
        input_data (dict): input data to be encoded into access token
    """
    token = create_access_token(input_data)
    output_data = decode_access_token(token)

    assert isinstance(input_data, dict)
    assert isinstance(token, str)
    assert isinstance(output_data, dict)

    assert output_data["username"] == input_data["username"]
    assert output_data["email"] == input_data["email"]
    assert output_data["permission_level"] == input_data["permission_level"]


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker
