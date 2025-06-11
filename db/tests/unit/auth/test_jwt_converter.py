from uuid import uuid4

import pytest

from db.auth.jwt_converter import jwt_to_data, data_to_jwt
from db.models.schemas import PermissionLevel, JWTokenData

# --- FIXTURES ---


@pytest.fixture(name="jwtokendata_data")
def jwtokendata_data_fixture():
    return {
        "uuid": str(uuid4()),
        "username": "testuser",
        "permission_level": PermissionLevel.USER
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
    data_to_jwt(jwtokendata)


def test_user_to_jwt_to_user_pass(jwtokendata: JWTokenData):
    """Check if decode of created access token is successful

    Args:
        jwtokendata (JWTokenData): data to include in token
    """
    token = data_to_jwt(jwtokendata)
    jwt_to_data(token)


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker
