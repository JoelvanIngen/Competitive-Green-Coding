import random

import pytest
import requests

from common.languages import Language
from common.schemas import AddProblemRequest, ProblemDetailsResponse, TokenResponse
from common.typing import Difficulty, PermissionLevel
from server.config import settings

NAMES = ["aap", "noot", "mies", "wim", "zus", "jet", "teun", "vuur", "gijs", "lam", "kees", "bok",
         "weide", "does", "hok", "duif", "schapen"]

URL = f"http://localhost:{settings.SERVER_PORT}/api"

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
        wrappers=[["dummyname", "dummywrapper"]]
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
        wrappers=[["dummyname", "dummywrapper"]]
    )


def _post_request(*args, **kwargs):
    with requests.session() as session:
        return session.post(*args, **kwargs)


def _get_request(*args, **kwargs):
    with requests.session() as session:
        return session.get(*args, **kwargs)


def admin_jwt():
    username = random.choice(NAMES) + str(random.randint(0, 99))
    admin_register_data = {
                        "username": username,
                        "email": f"{username}@hotmail.com",
                        "password": "password1234",
                        "permission_level": PermissionLevel.ADMIN,
                    }

    response = _post_request(f'{URL}/auth/register', json=admin_register_data)

    token_data = response.json()
    token_response = TokenResponse(**token_data)
    token = token_response.access_token
    return token


def test_get_problem_result(problem_data):
    """ Test that adding a problem returns the correct details. """
    jwt = admin_jwt()
    response = _post_request(
        f'{URL}/admin/add-problem',
        json=problem_data.model_dump(),
        headers={"token": jwt},
    )

    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
    problem_details = ProblemDetailsResponse(**response.json())

    response = _get_request(
        f'{URL}/problem?problem_id={problem_details.problem_id}',
        headers={"token": jwt},
    )

    assert response.status_code == 200, f"Expected 200 Created, got {response.status_code}"

    problem_details = ProblemDetailsResponse(**response.json())
    assert problem_details.problem_id is not None
    assert problem_details.name == problem_data.name
    assert problem_details.language == problem_data.language
    assert problem_details.difficulty == problem_data.difficulty
    assert set(problem_details.tags) == set(problem_data.tags)
    assert problem_details.short_description == problem_data.short_description
    assert problem_details.long_description == problem_data.long_description
    assert problem_details.template_code == problem_data.template_code
