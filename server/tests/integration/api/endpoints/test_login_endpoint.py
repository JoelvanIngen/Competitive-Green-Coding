import random

import pytest
import requests

from common.schemas import JWTokenData, TokenResponse
from common.typing import PermissionLevel
from common.auth import jwt_to_data
from server.config import settings

NAMES = [
    "aap",
    "noot",
    "mies",
    "wim",
    "zus",
    "jet",
    "teun",
    "vuur",
    "gijs",
    "lam",
    "kees",
    "bok",
    "weide",
    "does",
    "hok",
    "duif",
    "schapen",
]

URL = f"http://localhost:{settings.SERVER_PORT}/api"

random.seed(0)


def _post_request(*args, **kwargs):
    with requests.session() as session:
        return session.post(*args, **kwargs)


def _get_request(*args, **kwargs):
    with requests.session() as session:
        return session.get(*args, **kwargs)


@pytest.fixture(name="user_register_data")
def user_register_data_fixture():
    username = random.choice(NAMES) + str(random.randint(0, 99))
    password = "password1234"

    data = {"username": username, "email": f"{username}@hotmail.com", "password": password}

    return data


@pytest.fixture(name="admin_register_data")
def admin_register_data_fixture():
    username = random.choice(NAMES) + str(random.randint(0, 99))
    admin_register_data = {
                        "username": username,
                        "email": f"{username}@hotmail.com",
                        "password": "password1234",
                        "permission_level": PermissionLevel.ADMIN,
                    }

    return admin_register_data


@pytest.fixture(name="admin_jwt")
def admin_jwt_fixture(admin_register_data):
    """
    Fixture to create a JWT token for a user with permission level USER.
    """

    response = _post_request(f'{URL}/auth/register', json=admin_register_data)

    token_data = response.json()
    token_response = TokenResponse(**token_data)
    token = token_response.access_token
    return token


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)


def test_login_pass(user_register_data):
    response = _post_request(f"{URL}/auth/register", json=user_register_data)

    assert response.status_code == 201

    user_login_data = {
        "username": user_register_data["username"],
        "password": user_register_data["password"],
    }

    response = _post_request(f"{URL}/auth/login", json=user_login_data)

    assert response.status_code == 200


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


def test_username_validation_fail(user_register_data):
    user_login_data = {
        "username": random.choice(NAMES) + str(random.randint(0, 99)).zfill(32),
        "password": user_register_data["password"],
    }

    response = _post_request(f"{URL}/auth/login", json=user_login_data)

    assert response.status_code == 400

    detail = response.json()["detail"]
    type, description = detail["type"], detail["description"]

    assert type == "username"
    assert description == "Username does not match constraints"


def test_wrong_password_fail(user_register_data):
    response = _post_request(f"{URL}/auth/register", json=user_register_data)

    assert response.status_code == 201

    user_login_data = {"username": user_register_data["username"], "password": "wrongpassword"}

    response = _post_request(f"{URL}/auth/login", json=user_login_data)

    assert response.status_code == 400

    detail = response.json()["detail"]
    type, description = detail["type"], detail["description"]

    assert type == "invalid"
    assert description == "Invalid username or password"


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_login_result(user_register_data):
    response = _post_request(f"{URL}/auth/register", json=user_register_data)

    assert response.status_code == 201

    user_login_data = {
        "username": user_register_data["username"],
        "password": user_register_data["password"],
    }

    response = _post_request(f"{URL}/auth/login", json=user_login_data)

    assert response.status_code == 200

    token_response = response.json()
    assert token_response["token_type"] == "bearer"

    data = jwt_to_data(
        token_response["access_token"], settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
    )

    assert isinstance(data, JWTokenData)
    assert data.username == user_register_data["username"]
    assert data.permission_level == PermissionLevel.USER


def test_change_permission(user_register_data, admin_jwt):
    response = _post_request(f"{URL}/auth/register", json=user_register_data)
    assert response.status_code == 201

    change_permission_data = {
        "username": user_register_data["username"],
        "permission": PermissionLevel.ADMIN,
    }

    response = _post_request(
        f'{URL}/admin/change-permission',
        change_permission_data,
        headers={'token': admin_jwt})

    # user_login_data = {
    #     "username": user_register_data["username"],
    #     "password": user_register_data["password"],
    # }

    response = _get_request(f"{URL}/users/me", headers={"Authorization": f"Bearer {admin_jwt}"})

    assert response.json()['details'] == 200

    user_response = response.json()
    # token = token_response["access_token"]

    # user_data = jwt_to_data(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

    assert user_response.permission_level == PermissionLevel.ADMIN
