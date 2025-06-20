import pytest
import requests
import random

from common.schemas import ProblemsListResponse
from common.schemas import PermissionLevel
from server.config import settings

URL = f"http://localhost:{settings.SERVER_PORT}/api"

def _post_request(*args, **kwargs):
    with requests.session() as session:
        return session.post(*args, **kwargs)


@pytest.fixture(scope="module")
def create_admin_token():
    """
    Creates an admin user and returns a JWT token for that user.
    This fixture is used to authenticate requests to the API endpoints that require admin permissions.
    """
    username = "adminsimon" + str(random.randint(0, 10000))
    password = "simon_123"

    register_data = {
        "username": username,
        "email": f"{username}@simon.com",
        "password": password,
        "permission_level": PermissionLevel.ADMIN,
    }

    response = _post_request(f"{URL}/auth/register", json=register_data)
    assert response.status_code == 201

    login_data = {
        "username": username,
        "password": password,
    }

    response = _post_request(f"{URL}/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def create_problem(create_admin_token):
    """
    Creates a problem using the admin token provided by the create_admin_token fixture.
    This fixture is used to ensure that a problem exists for testing the API endpoints.
    """
    headers = {"token": f"{create_admin_token}"}


    problem_data = {
        "name": "IntegrationTestProblem" + str(random.randint(0, 10000)),
        "language": "python",
        "difficulty": "easy",
        "tags": ["test"],
        "short_description": "Short test desc",
        "long_description": "Long test desc",
        "template_code": "def main(): pass"
    }

    response = _post_request(f"{URL}/admin/add-problem", json=problem_data, headers=headers)

    if response.status_code != 200:
        print("STATUS:", response.status_code)
        print("BODY:", response.json())

    assert response.status_code == 200


# --- SPECIAL CASE: CRASH TEST for empty DB ---
# This test must run before any problems are inserted (before fixtures are triggered).
def test_problems_zero_problems_fail():
    response = _post_request(f"{URL}/problems/all", json={"limit": 10})

    assert response.status_code == 400

    detail = response.json()["detail"]
    assert detail["type"] == "not_found"
    assert detail["description"] == "Problems not found"


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)
def test_problems_all_pass(create_problem):
    response = _post_request(f"{URL}/problems/all", json={"limit": 10})

    assert response.status_code == 200


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here
def test_problems_all_invalid_limit_fail():
    response = _post_request(f"{URL}/problems/all", json={"limit": -5})
    assert response.status_code == 400

    detail = response.json()["detail"]
    assert detail["type"] == "not_found"
    assert detail["description"] == "Problems not found"


def test_problems_all_excessive_limit_fail():
    response = _post_request(f"{URL}/problems/all", json={"limit": 99999})
    assert response.status_code == 400

    detail = response.json()["detail"]
    assert detail["type"] == "not_found"
    assert detail["description"] == "Problems not found"


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or resultd
def test_problems_all_result(create_problem):
    response = _post_request(f"{URL}/problems/all", json={"limit": 10})
    assert response.status_code == 200

    data = response.json()

    assert "total" in data
    assert "problems" in data
    assert isinstance(data["total"], int)
    assert isinstance(data["problems"], list)

    if data["problems"]:
        first = data["problems"][0]
        assert "problem-id" in first
        assert "name" in first
        assert "difficulty" in first
        assert "short-description" in first