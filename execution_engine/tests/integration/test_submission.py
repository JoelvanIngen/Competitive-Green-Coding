from datetime import datetime
from uuid import UUID, uuid4

import pytest
import requests

from common.languages import Language
from common.schemas import SubmissionCreate

CODE = \
"""
int add_one(int num) {
    return num + 1;
}
"""


@pytest.fixture(name="execution_request")
def execution_request_fixture():
    return SubmissionCreate(
        submission_uuid=uuid4(),
        problem_id=10000,
        user_uuid=UUID("00000000-0000-0000-0000-000000000000"),
        language=Language.C,
        timestamp=int(datetime.now().timestamp()),
        code=CODE,
    )


def test_create_submission_ok(execution_request):
    res = requests.post(
        "http://localhost:8080/api/execute",
        data=execution_request.model_dump_json(),
        headers={"Content-Type": "application/json"},
    )
    assert res.status_code == 201
