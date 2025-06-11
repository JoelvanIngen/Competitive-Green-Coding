import datetime
import pytest
from uuid import UUID

from db.models.db_schemas import UserEntry, SubmissionEntry, ProblemEntry
from db.models.schemas import (
    PermissionLevel,
    UserGet,
    SubmissionPost,
    SubmissionGet,
    ProblemGet,
)

""""
I've written fixtures for all three (current) possible schemas that
src/db/models/convert.py could ecounter.
"""


@pytest.fixture
def sample_user_entry():
    return UserEntry(
        uuid=UUID("fae21-brz9k1-23olnn"),
        username="marouan",
        email="marouan@test.com",
        permission_level=PermissionLevel.USER,
    )


@pytest.fixture
def expected_user_get(sample_user_entry):
    return UserGet(
        uuid=sample_user_entry.uuid,
        username=sample_user_entry.username,
        email=sample_user_entry.email,
        permission_level=PermissionLevel.USER,
    )


@pytest.fixture
def sample_submission_post():
    return SubmissionPost(
        problem_id=42,
        uuid=UUID("asd123ac-asd1231-hj1234"),
        runtime_ms=8432,
        timestamp=1620000000,
        successful=True,
        code="print('this is a pytest!!!')",
    )


@pytest.fixture
def sample_submission_entry(sample_submission_post):
    return SubmissionEntry(
        problem_id=sample_submission_post.problem_id,
        uuid=sample_submission_post.uuid,
        runtime_ms=sample_submission_post.runtime_ms,
        timestamp=sample_submission_post.timestamp,
        successful=sample_submission_post.successful,
    )


@pytest.fixture
def sample_db_submission_for_get():
    return SubmissionEntry(
        sid=1,
        problem_id=42,
        uuid=UUID("asda123-8912az-10123kr"),
        score=100,
        timestamp=1620000000,
        successful=False,
    )


@pytest.fixture
def expected_submission_get(sample_db_submission_for_get):
    return SubmissionGet(
        sid=sample_db_submission_for_get.sid,
        problem_id=sample_db_submission_for_get.problem_id,
        uuid=sample_db_submission_for_get.uuid,
        score=sample_db_submission_for_get.score,
        timestamp=sample_db_submission_for_get.timestamp,
        successful=sample_db_submission_for_get.successful,
        code="",
    )


@pytest.fixture
def sample_problem_entry():
    return ProblemEntry(
        problem_id=7,
        name="Impossible problem",
        description="Will program x halt?",
    )


@pytest.fixture
def expected_problem_get(sample_problem_entry):
    return ProblemGet(
        problem_id=sample_problem_entry.problem_id,
        name=sample_problem_entry.name,
        tags=[],
        description=sample_problem_entry.description,
    )
