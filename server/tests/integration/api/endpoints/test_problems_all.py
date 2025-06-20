import pytest
import requests

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

    assert response.status_code == 200


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here
