import random

import pytest
import requests

import os
from common.languages import Language
from common.schemas import AddProblemRequest, TokenResponse, ProblemDetailsResponse
# from common.auth import jwt_to_data
from common.typing import PermissionLevel, Difficulty
from server.config import settings

NAMES = ["aap", "noot", "mies", "wim", "zus", "jet", "teun", "vuur", "gijs", "lam", "kees", "bok",
         "weide", "does", "hok", "duif", "schapen"]

URL = f"http://localhost:{settings.SERVER_PORT}/api"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))

WRAPPER_BASE_PATH = os.path.join(PROJECT_ROOT, "storage-example", "wrappers")

random.seed(0)


@pytest.fixture(name="user_register_data")
def user_register_data_fixture():
    username = random.choice(NAMES) + str(random.randint(0, 99))
    user_register_data = {
                        "username": username,
                        "email": f"{username}@hotmail.com",
                        "password": "password1234",
                        "permission_level": PermissionLevel.USER,
                    }

    return user_register_data


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

    # user_data = JWTokenData(
    #     uuid="2",
    #     username="testuser",
    #     permission_level=PermissionLevel.USER,
    # )

    # return data_to_jwt(user_data)


# @pytest.fixture(name="admin_register_data")
# def admin_register_data_fixture():
#     username = random.choice(NAMES) + str(random.randint(0, 99))
#     admin_register_data = {
#                         "username": username,
#                         "email": f"{username}@hotmail.com",
#                         "password": "password1234",
#                         "permission_level": PermissionLevel.ADMIN,
#                     }

#     return admin_register_data

    # admin_data = JWTokenData(
    #     uuid="1",
    #     username="testadmin",
    #     permission_level=PermissionLevel.ADMIN,
    # )

    # return data_to_jwt(admin_data)


@pytest.fixture(name="problem_data")
def problem_data_fixture():
    return AddProblemRequest(
        name="Test Problem",
        language=Language.PYTHON,
        difficulty=Difficulty.EASY,
        tags=["test", "example"],
        short_description="A simple test problem.",
        long_description="This is a longer description of the test problem.",
        template_code="# Write your solution here",
        wrapper=["a random wrapper"]
    )


@pytest.fixture(name="problem_data2")
def problem2_data_fixture():
    return AddProblemRequest(
        name="Test Problem2",
        language=Language.PYTHON,
        difficulty=Difficulty.EASY,
        tags=["test", "example"],
        short_description="A simple test problem2.",
        long_description="This is a longer description of the test problem2.",
        template_code="# Write your solution here",
        wrapper=["a random wrapper"]
    )


# def test_tokenresponse(user_register_data):
#     response = _post_request(f'{URL}/auth/register', json=user_register_data)

#     token_data = response.json()
#     token_response = TokenResponse(**token_data)

#     assert isinstance(token_response, TokenResponse)


# def test_token_permission(admin_jwt, user_jwt):
#     admin_data = jwt_to_data(admin_jwt, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
#     user_data = jwt_to_data(user_jwt, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

#     assert admin_data.permission_level == PermissionLevel.ADMIN
#     assert user_data.permission_level == PermissionLevel.USER


def _post_request(*args, **kwargs):
    with requests.session() as session:
        return session.post(*args, **kwargs)


# def admin_jwt():
#     username = random.choice(NAMES) + str(random.randint(0, 99))
#     admin_register_data = {
#                         "username": username,
#                         "email": f"{username}@hotmail.com",
#                         "password": "password1234",
#                         "permission_level": PermissionLevel.ADMIN,
#                     }

#     response = _post_request(f'{URL}/auth/register', json=admin_register_data)

#     token_data = response.json()
#     token_response = TokenResponse(**token_data)
#     token = token_response.access_token
#     return token


def test_add_problem_pass(problem_data, admin_jwt):
    response = _post_request(
                            f'{URL}/admin/add-problem',
                            json=problem_data.model_dump(),
                            headers={"token": admin_jwt}
                            )

    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"


def test_add_problem_result(problem_data, admin_jwt):
    """ Test that adding a problem returns the correct details. """
    response = _post_request(
                            f'{URL}/admin/add-problem',
                            json=problem_data.model_dump(),
                            headers={"token": admin_jwt}
                            )

    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"

    problem_details = ProblemDetailsResponse(**response.json())
    assert problem_details.problem_id is not None
    assert problem_details.name == problem_data.name
    assert problem_details.language == problem_data.language
    assert problem_details.difficulty == problem_data.difficulty
    assert set(problem_details.tags) == set(problem_data.tags)
    assert problem_details.short_description == problem_data.short_description
    assert problem_details.long_description == problem_data.long_description
    assert problem_details.template_code == problem_data.template_code


def test_add_problem_no_auth(problem_data, user_jwt):
    """
    Test that adding a problem without authentication fails.
    """
    jwt = user_jwt
    response = _post_request(
                            f'{URL}/admin/add-problem',
                            json=problem_data.model_dump(),
                            headers={"token": jwt}
                            )

    assert response.status_code == 401

    detail = response.json()['detail']
    type, description = detail["type"], detail["description"]

    assert type == "unauthorized"
    assert description == "User does not have admin permissions"


def test_add_problem_wrapper(problem_data, admin_jwt):
    """
    Test that the add_problem endpoint works as expected.
    This is a wrapper function to ensure the test runs correctly.
    """
    response = _post_request(
                            f'{URL}/admin/add-problem',
                            json=problem_data.model_dump(),
                            headers={"token": admin_jwt}
                            )

    assert response.status_code == 201
    problem_details = ProblemDetailsResponse(**response.json())
    assert problem_details.wrapper == problem_data.wrapper


def test_add_multiple_problems(problem_data, problem_data2, admin_jwt):
    """
    Test adding multiple problems to ensure the endpoint can handle multiple requests.
    """
    response1 = _post_request(
                            f'{URL}/admin/add-problem',
                            json=problem_data.model_dump(),
                            headers={"token": admin_jwt}
    )
    assert response1.status_code == 201

    response2 = _post_request(
                            f'{URL}/admin/add-problem',
                            json=problem_data2.model_dump(),
                            headers={"token": admin_jwt}
    )
    assert response2.status_code == 201
