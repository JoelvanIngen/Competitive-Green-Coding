import pytest
import requests

from server.config import settings

URL = f"http://localhost:{settings.SERVER_PORT}/api"


def _post_request(*args, **kwargs):
    with requests.session() as session:
        return session.post(*args, **kwargs)

