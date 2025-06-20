import random

import pytest
import requests

from common.schemas import AddProblemRequest, TokenResponse
from server.auth import data_to_jwt
from common.typing import PermissionLevel
from server.config import settings


URL = f"http://localhost:{settings.SERVER_PORT}/api"

random.seed(0)


@pytest.fixture(name="user_register_data")
def user_register_data_fixture():
    user_register_data = {
                        "username": "testuser",
                        "email": "testuser@gmail.com",
                        "password": "password1234",
                        "permission_level": PermissionLevel.USER,
                    }

    return user_register_data


@pytest.fixture(name="user_jwt")
def user_jwt_fixture(user_register_data):
    """
    Fixture to create a JWT token for a user with permission level USER.
    """

    response = _post_request(f'{URL}/auth/register', json=user_register_data)

    token_data = response.json()
    token_response = TokenResponse(**token_data)
    token = token_response.access_token
    return token


@pytest.fixture(name="admin_register_data")
def admin_register_data_fixture():
    admin_register_data = {
                        "username": "testadmin",
                        "email": "testadmin@gmail.com",
                        "password": "password1234",
                        "permission_level": PermissionLevel.ADMIN,
                    }

    return admin_register_data


@pytest.fixture(name="admin_jwt")
def admin_jwt_fixture(admin_register_data):
    """
    Fixture to create a JWT token for a user with permission level USER.
    """

    # response = _post_request(f'{URL}/auth/register', json=admin_register_data)

    # token_data = response.json()
    # token_response = TokenResponse(**token_data)
    # token = token_response.access_token
    # return token

    admin_data = {
        "uuid": "1",
        "username": "testadmin",
        "permission_level": PermissionLevel.ADMIN,
    }

    return data_to_jwt(admin_data)


@pytest.fixture(name="problem_data")
def problem_data_fixture():
    return AddProblemRequest(
        name="Test Problem",
        language="python",
        difficulty="easy",
        tags=["test", "example"],
        short_description="A simple test problem.",
        long_description="This is a longer description of the test problem.",
        template_code="# Write your solution here",
    )


@pytest.fixture(name="faulty_difficulty_problem_data")
def faulty_difficulty_problem_fixture():
    return AddProblemRequest(
        name="Test Problem",
        language="python",
        difficulty="tough",
        tags=["test", "example"],
        short_description="A simple test problem.",
        long_description="This is a longer description of the test problem.",
        template_code="# Write your solution here",
    )


def test_tokenresponse(user_register_data):
    response = _post_request(f'{URL}/auth/register', json=user_register_data)

    token_data = response.json()
    token_response = TokenResponse(**token_data)

    assert isinstance(token_response, TokenResponse)


def _post_request(*args, **kwargs):
    with requests.session() as session:
        return session.post(*args, **kwargs)


def test_add_problem_pass(problem_data, admin_jwt):
    response = _post_request(
                            f'{URL}/problems/add',
                            json=problem_data.dict(),
                            headers={"Authorization": f"Bearer {admin_jwt}"})

    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"


def test_add_problem_result(problem_data, admin_jwt):
    response = _post_request(
                            f'{URL}/problems/add',
                            json=problem_data.dict(),
                            headers={"Authorization": f"Bearer {admin_jwt}"}
                            )

    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"

    resp = response.json()['detail']

    assert resp.problem_id is not None
    assert resp.name == problem_data.name
    assert resp.language == problem_data.language
    assert resp.difficulty == problem_data.difficulty
    assert resp.tags == problem_data.tags
    assert resp.short_description == problem_data.short_description
    assert resp.long_description == problem_data.long_description
    assert resp.template_code == problem_data.template_code


def test_faulty_difficulty_problem(faulty_difficulty_problem_data, admin_jwt):
    response = _post_request(
                            f'{URL}/problems/add',
                            json=faulty_difficulty_problem_data.dict(),
                            headers={"Authorization": f"Bearer {admin_jwt}"}
                            )

    assert response.status_code == 400

    detail = response.json()['detail']
    type, description = detail["type"], detail["description"]

    assert type == "validation"
    assert description == "Title is required\nDifficulty must be one of: easy, medium, hard"


def test_add_problem_no_auth(problem_data, user_jwt):
    """
    Test that adding a problem without authentication fails.
    """
    response = _post_request(
                            f'{URL}/problems/add',
                            json=problem_data.dict(),
                            headers={"Authorization": f"Bearer {user_jwt}"}
                            )

    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

    detail = response.json()['detail']
    type, description = detail["type"], detail["description"]

    assert type == "unauthorized"
    assert description == "User does not have admin permissions"
