import pytest
import requests

from common.schemas import ProblemsListResponse

from server.config import settings

URL = f"http://localhost:{settings.SERVER_PORT}/api"


def _post_request(*args, **kwargs):
    with requests.session() as session:
        return session.post(*args, **kwargs)


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)
def test_problems_all_pass():
    response = _post_request(f"{URL}/problems/all", json={"limit": 10})

    assert response.status_code == 400


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here
def test_problems_all_invalid_limit_fail():
    response = _post_request(f"{URL}/problems/all", json={"limit": -5})
    assert response.status_code == 400

    detail = response.json()["detail"]
    assert detail["type"] ==  "other"
    assert detail["description"] == "An unexpected error occured"

def test_problems_all_excessive_limit_fail():
    response = _post_request(f"{URL}/problems/all", json={"limit": 99999})
    assert response.status_code == 400

    detail = response.json()["detail"]
    assert detail["type"] ==  "other"
    assert detail["description"] == "An unexpected error occured"


def test_problems_no_problems_fail(mocker):
    mock_result = ProblemsListResponse(total=0, problems=[])
    mocker.patch("db.api.modules.actions.ops.get_problem_metadata", return_value=mock_result)

    response = _post_request(f"{URL}/problems/all", json={"limit": 10})

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["type"] ==  "other"
    assert detail["description"] == "An unexpected error occured"

# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or resultd

def test_problems_all_result():
    response = _post_request(f"{URL}/problems/all", json={"limit": 5})
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