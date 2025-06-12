import pytest

from db.models.db_schemas import UserEntry, SubmissionEntry, ProblemEntry
from db.models.schemas import (
    PermissionLevel,
    UserGet,
    SubmissionPost,
    SubmissionGet,
    ProblemGet,
)


@pytest.fixture
def submission_post_missing_runtime_fixture():
    return {
        "problem_id": 42,
        "uuid": "d737eaf5-25d0-41cc-80f8-ca2adafff53a",
        "timestamp": 1620000000,
        "successful": True,
        "code": "print('no runtime!')",
    }


@pytest.fixture
def user_entry_fixture():
    return UserEntry(
        uuid="d737eaf5-25d0-41cc-80f8-ca2adafff53a",
        username="marouan",
        email="marouan@test.com",
        permission_level=PermissionLevel.USER,
    )


@pytest.fixture
def user_get_fixture(user_entry_fixture):
    return UserGet(
        uuid=user_entry_fixture.uuid,
        username=user_entry_fixture.username,
        email=user_entry_fixture.email,
        permission_level=PermissionLevel.USER,
    )


@pytest.fixture
def submission_post_fixture():
    return SubmissionPost(
        problem_id=42,
        uuid="1fac3060-f853-4e1b-8ebd-b66014af8dc0",
        runtime_ms=8432,
        timestamp=1620000000,
        successful=True,
        code="print('this is a pytest!!!')",
    )


@pytest.fixture
def submission_entry_fixture(submission_post_fixture):
    return SubmissionEntry(
        problem_id=submission_post_fixture.problem_id,
        uuid=submission_post_fixture.uuid,
        runtime_ms=submission_post_fixture.runtime_ms,
        timestamp=submission_post_fixture.timestamp,
        successful=submission_post_fixture.successful,
    )


@pytest.fixture
def db_submission_for_get_fixture():
    return SubmissionEntry(
        sid=1,
        problem_id=42,
        uuid="3603233c-94fc-4303-83c4-829ffec05739",
        score=100,
        timestamp=1620000000,
        successful=False,
    )


@pytest.fixture
def submission_get_fixture(db_submission_for_get_fixture):
    return SubmissionGet(
        sid=db_submission_for_get_fixture.sid,
        problem_id=db_submission_for_get_fixture.problem_id,
        uuid=db_submission_for_get_fixture.uuid,
        score=db_submission_for_get_fixture.score,
        timestamp=db_submission_for_get_fixture.timestamp,
        successful=db_submission_for_get_fixture.successful,
        code="",
    )


@pytest.fixture
def problem_entry_fixture():
    return ProblemEntry(
        problem_id=7,
        name="Impossible problem",
        description="Will program x halt?",
    )


@pytest.fixture
def problem_get_fixture(problem_entry_fixture):
    return ProblemGet(
        problem_id=problem_entry_fixture.problem_id,
        name=problem_entry_fixture.name,
        tags=[],
        description=problem_entry_fixture.description,
    )
