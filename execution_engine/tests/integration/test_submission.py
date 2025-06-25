from datetime import datetime
from uuid import UUID, uuid4

import pytest
import requests

from common.languages import Language
from common.schemas import SubmissionCreate, SubmissionResult


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


@pytest.fixture(name="execution_result")
def execution_result_fixture():
    return SubmissionResult(
        submission_uuid=uuid4(),
        runtime_ms=123.456,
        mem_usage_mb=10.5,
        energy_usage_kwh=0.001,
        successful=True,
        error_reason=None,
        error_msg=None,
    )


def test_create_submission_ok(execution_request):
    res = requests.post(
        "http://localhost:8080/api/execute",
        data=execution_request.model_dump_json(),
        headers={"Content-Type": "application/json"},
    )
    assert res.status_code == 201


def test_update_submission(execution_request, execution_result):
    res = requests.post(
        "http://localhost:8080/api/execute",
        data=execution_request.model_dump_json(),
        headers={"Content-Type": "application/json"},
    )
    assert res.status_code == 201

    execution_result.submission_uuid = execution_request.submission_uuid
    res = requests.post(
        "http://localhost:8080/api/write-submission-result",
        data=execution_result.model_dump_json(),
        headers={"Content-Type": "application/json"},
    )
    assert res.status_code == 201
