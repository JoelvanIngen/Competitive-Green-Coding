import random

import pytest
import requests

from common.schemas import JWTokenData
from common.typing import PermissionLevel
from common.auth import jwt_to_data
from server.config import settings

NAMES = ["aap", "noot", "mies", "wim", "zus", "jet", "teun", "vuur", "gijs", "lam", "kees", "bok",
         "weide", "does", "hok", "duif", "schapen"]

URL = f"http://localhost:{settings.SERVER_PORT}/api"

random.seed(0)


def _post_request(*args, **kwargs):
    with requests.session() as session:
        return session.post(*args, **kwargs)


@pytest.fixture(name="user_register_data")
def user_register_data_fixture():
    username = random.choice(NAMES) + str(random.randint(0, 99))
    password = "password1234"

    data = {
        "username": username,
        "email": f"{username}@hotmail.com",
        "password": password
    }

    return data


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)


def test_register_pass(user_register_data):
    response = _post_request(f'{URL}/auth/register', json=user_register_data)

    assert response.status_code == 201


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


def test_username_in_use_fail(user_register_data):
    response = _post_request(f'{URL}/auth/register', json=user_register_data)

    assert response.status_code == 201

    user_register_data["email"] = "different_email@hotmail.com"
    response = _post_request(f'{URL}/auth/register', json=user_register_data)

    assert response.status_code == 400

    detail = response.json()["detail"]
    type, description = detail["type"], detail["description"]

    assert type == "username"
    assert description == "Username already in use"


def test_email_in_use_fail(user_register_data):
    response = _post_request(f'{URL}/auth/register', json=user_register_data)

    assert response.status_code == 201

    user_register_data["username"] = random.choice(NAMES) + str(random.randint(0, 99))
    response = _post_request(f'{URL}/auth/register', json=user_register_data)

    assert response.status_code == 400

    detail = response.json()["detail"]
    type, description = detail["type"], detail["description"]

    assert type == "email"
    assert description == "There already exists an account associated to this email"


def test_username_validation_fail(user_register_data):
    user_register_data["username"] = random.choice(NAMES) + str(random.randint(0, 99)).zfill(32)
    response = _post_request(f'{URL}/auth/register', json=user_register_data)

    assert response.status_code == 400

    detail = response.json()["detail"]
    type, description = detail["type"], detail["description"]

    assert type == "username"
    assert description == "Username does not match constraints"

    user_register_data["username"] = random.choice(NAMES) + str(random.randint(0, 99)) + "!"
    response = _post_request(f'{URL}/auth/register', json=user_register_data)

    assert response.status_code == 400

    detail = response.json()["detail"]
    type, description = detail["type"], detail["description"]

    assert type == "username"
    assert description == "Username does not match constraints"


def test_email_validation_fail(user_register_data):
    user_register_data["email"] = "not_an_email"
    response = _post_request(f'{URL}/auth/register', json=user_register_data)

    assert response.status_code == 400

    detail = response.json()["detail"]
    type, description = detail["type"], detail["description"]

    assert type == "email"
    assert description == "Invalid email format"


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result

def test_register_result(user_register_data):
    response = _post_request(f'{URL}/auth/register', json=user_register_data)

    assert response.status_code == 201

    token_response = response.json()
    assert token_response["token_type"] == "bearer"

    data = jwt_to_data(
        token_response["access_token"],
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    )

    assert isinstance(data, JWTokenData)
    assert data.username == user_register_data["username"]
    assert data.permission_level == PermissionLevel.USER
