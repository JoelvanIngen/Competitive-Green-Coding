"""
Integration tests for the remove problem endpoint.
These tests check the functionality of the /admin/remove-problem endpoint, including:
- Successful removal of a problem by an admin
- Handling of non-existent problems
- Unauthorized access by non-admin users
- Validation of problem_id input
- Handling of missing authentication tokens
"""
import random
import requests
import pytest

from common.typing import PermissionLevel
from server.config import settings

URL = f"http://localhost:{settings.SERVER_PORT}/api"
NAMES = ["aap", "noot", "mies", "wim", "zus", "jet", "teun", "vuur", "gijs", "lam", "kees", "bok"]


def _post_request(*args, **kwargs):
    with requests.session() as session:
        return session.post(*args, **kwargs)

# ------------------------- Fixtures -------------------------


@pytest.fixture(name="admin_jwt")
def admin_jwt_fixture():
    """Registers an admin user and returns a valid JWT token."""
    username = random.choice(NAMES) + str(random.randint(1000, 9999))
    response = _post_request(f"{URL}/auth/register", json={
        "username": username,
        "email": f"{username}@simon.com",
        "password": "password1234",
        "permission_level": PermissionLevel.ADMIN,
    })
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.fixture(name="user_jwt")
def user_jwt_fixture():
    """Registers a normal user and returns a valid JWT token."""
    username = random.choice(NAMES) + str(random.randint(1000, 9999))
    response = _post_request(f"{URL}/auth/register", json={
        "username": username,
        "email": f"{username}@simon.com",
        "password": "password1234",
        "permission_level": PermissionLevel.USER,
    })
    assert response.status_code == 201
    return response.json()["access_token"]

# ------------------------- Helpers -------------------------


def create_problem_and_get_id(token: str) -> int:
    """Creates a new problem and returns its problem_id."""
    problem = {
        "name": "IntegrationRemoveProblem" + str(random.randint(0, 10000)),
        "language": "python",
        "difficulty": "easy",
        "tags": ["test"],
        "short_description": "Short test desc",
        "long_description": "Long test desc",
        "template_code": "def main(): pass",
        "wrappers": [["dummyname", "dummywrapper"]],
    }
    response = _post_request(
        f"{URL}/admin/add-problem",
        json=problem,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    return response.json()["problem_id"]

# ------------------------- Tests -------------------------


def test_remove_problem_success(admin_jwt):
    """
    Admin successfully deletes an existing problem.
    """
    pid = create_problem_and_get_id(admin_jwt)
    response = _post_request(
        f"{URL}/admin/remove-problem",
        json={"problem_id": pid},
        headers={"token": admin_jwt}
    )

    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["problem_id"] == pid
    assert data["deleted"] is True


def test_remove_problem_not_found(admin_jwt):
    """
    Deleting a non-existent problem should return 404.
    """
    response = _post_request(
        f"{URL}/admin/remove-problem",
        json={"problem_id": 999999},
        headers={"token": admin_jwt}
    )
    assert response.status_code == 404
    data = response.json()["detail"]
    assert data["type"] == "problem"
    assert data["description"] == "Problem not found"


def test_remove_problem_not_admin(user_jwt):
    """
    A non-admin user should be rejected (401).
    """
    response = _post_request(
        f"{URL}/admin/remove-problem",
        json={"problem_id": 1},
        headers={"token": user_jwt}
    )
    assert response.status_code == 401
    data = response.json()["detail"]
    assert data["type"] == "unauthorized"


def test_remove_problem_invalid_id(admin_jwt):
    """
    Negative problem_id should trigger 400 validation error.
    """
    response = _post_request(
        f"{URL}/admin/remove-problem",
        json={"problem_id": -1},
        headers={"token": admin_jwt}
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert isinstance(response.json()["detail"], list)


def test_remove_problem_missing_token():
    """
    Missing token should return 401 or 422 depending on FastAPI validation order.
    """
    response = _post_request(
        f"{URL}/admin/remove-problem",
        json={"problem_id": 1}
    )
    assert response.status_code in [401, 422]
