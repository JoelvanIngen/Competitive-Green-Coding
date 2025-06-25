import random

import pytest
import requests

from common.languages import Language
from common.schemas import (
    AddProblemRequest,
    ProblemDetailsResponse,
    SubmissionRequest,
    TokenResponse,
    SubmissionCreateResponse,
)
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


@pytest.fixture(name="submission_request_data")
def submission_request_data_fixture(problem_data: AddProblemRequest):
    return {
        "problem_id": 0,
        "language": problem_data.language,
        "code": "test_submission_code"
    }


@pytest.fixture(name="submission_request")
def submission_request_fixture(submission_request_data):
    return SubmissionRequest(**submission_request_data)


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


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


def test_submission_problem_not_found_fail(
    user_jwt: str,
    submission_request: SubmissionRequest
):
    """ Test that adding a problem returns the correct details. """
    response = _post_request(
        f'{URL}/submission',
        json=submission_request.model_dump(),
        headers={"token": user_jwt},
    )

    assert response.status_code == 404

    detail = response.json()["detail"]
    type, description = detail["type"], detail["description"]

    assert type == "problem"
    assert description == "Problem not found"


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_submission_result(
    problem_data: AddProblemRequest,
    user_jwt: str,
    submission_request: SubmissionRequest
):
    """Test submission is successfully added."""
    jwt = admin_jwt()
    response = _post_request(
        f'{URL}/admin/add-problem',
        json=problem_data.model_dump(),
        headers={"token": jwt},
    )

    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
    problem_details = ProblemDetailsResponse(**response.json())

    submission_request.problem_id = problem_details.problem_id

    response = _post_request(
        f'{URL}/submission',
        json=submission_request.model_dump(),
        headers={"token": user_jwt},
    )

    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"

    submission = SubmissionCreateResponse(**response.json())
    assert submission.submission_uuid is not None


def test_get_problem_submission_result(
    problem_data: AddProblemRequest,
    user_jwt: str,
    submission_request: SubmissionRequest,
):
    """Test that retrieving problem with previous submission returns submission."""
    jwt = admin_jwt()
    response = _post_request(
        f'{URL}/admin/add-problem',
        json=problem_data.model_dump(),
        headers={"token": jwt},
    )

    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
    problem_details = ProblemDetailsResponse(**response.json())

    submission_request.problem_id = problem_details.problem_id

    response = _post_request(
        f'{URL}/submission',
        json=submission_request.model_dump(),
        headers={"token": user_jwt},
    )

    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"

    submission = SubmissionCreateResponse(**response.json())

    response = _get_request(
        f'{URL}/problem?problem_id={problem_details.problem_id}',
        headers={"token": user_jwt},
    )

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    problem_details = ProblemDetailsResponse(**response.json())
    assert problem_details.template_code == submission_request.code
    assert problem_details.submission_id == submission.submission_uuid
