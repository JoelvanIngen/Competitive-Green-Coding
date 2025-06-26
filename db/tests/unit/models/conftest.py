from uuid import UUID
import pytest
from common.languages import Language
from common.typing import PermissionLevel, ErrorReason

from common.schemas import (
    UserGet,
    AddProblemRequest,
    ProblemDetailsResponse,
    SubmissionCreate,
    SubmissionMetadata,
    SubmissionFull,
    SubmissionResult,
    JWTokenData,
)
from db.models.db_schemas import UserEntry, SubmissionEntry, ProblemEntry, ProblemTagEntry


@pytest.fixture
def user_entry_fixture():
    return UserEntry(
        uuid=UUID("d737eaf5-25d0-41cc-80f8-ca2adafff53a"),
        username="marouan",
        email="marouan@test.com",
        permission_level=PermissionLevel.USER,
        hashed_password=b"hashed_password",
    )


@pytest.fixture
def user_get_fixture():
    return UserGet(
        uuid=UUID("d737eaf5-25d0-41cc-80f8-ca2adafff53a"),
        username="marouan",
        email="marouan@test.com",
        permission_level=PermissionLevel.USER,
        avatar_id=0,
        private=False,
    )


@pytest.fixture
def submission_create_fixture():
    return SubmissionCreate(
        submission_uuid=UUID("1fac3060-f853-4e1b-8ebd-b66014af8dc0"),
        problem_id=42,
        user_uuid=UUID("d737eaf5-25d0-41cc-80f8-ca2adafff53a"),
        language=Language.PYTHON,
        timestamp=1620000000,
        code="print('this is a pytest!!!')",
    )


@pytest.fixture
def submission_entry_fixture():
    return SubmissionEntry(
        submission_uuid=UUID("3603233c-94fc-4303-83c4-829ffec05739"),
        problem_id=42,
        user_uuid=UUID("d737eaf5-25d0-41cc-80f8-ca2adafff53a"),
        language=Language.PYTHON,
        runtime_ms=8432.12,
        emissions_kg=128.5,
        energy_usage_kwh=0.0,
        timestamp=1620000000,
        executed=True,
        successful=False,
        error_reason=ErrorReason.RUNTIME_ERROR,
        error_msg="test error message",
    )


@pytest.fixture
def submission_result_fixture():
    return SubmissionResult(
        submission_uuid=UUID("3603233c-94fc-4303-83c4-829ffec05739"),
        runtime_ms=8432.12,
        emissions_kg=128.5,
        energy_usage_kwh=0.0,
        successful=False,
        error_reason=ErrorReason.RUNTIME_ERROR,
        error_msg="test error message",
    )


@pytest.fixture
def submission_metadata_fixture():
    return SubmissionMetadata(
        submission_uuid=UUID("3603233c-94fc-4303-83c4-829ffec05739"),
        problem_id=42,
        user_uuid=UUID("d737eaf5-25d0-41cc-80f8-ca2adafff53a"),
        language=Language.PYTHON,
        runtime_ms=8432.12,
        emissions_kg=128.5,
        energy_usage_kwh=0.0,
        timestamp=1620000000,
        executed=True,
        successful=False,
        error_reason=ErrorReason.RUNTIME_ERROR,
    )


@pytest.fixture
def submission_full_fixture():
    return SubmissionFull(
        submission_uuid=UUID("3603233c-94fc-4303-83c4-829ffec05739"),
        problem_id=42,
        user_uuid=UUID("d737eaf5-25d0-41cc-80f8-ca2adafff53a"),
        language=Language.PYTHON,
        runtime_ms=8432.12,
        emissions_kg=128.5,
        energy_usage_kwh=0.0,
        timestamp=1620000000,
        executed=True,
        successful=False,
        error_reason=ErrorReason.RUNTIME_ERROR,
        error_msg="test error message",
        code="",
    )


@pytest.fixture
def problem_post_fixture():
    return AddProblemRequest(
        name="Test Problem",
        language=Language.PYTHON,
        difficulty="medium",
        tags=["test", "array"],
        short_description="Short description",
        long_description="Long description",
        template_code="def solution(): pass",
        wrappers=[["dummyname", "dummywrapper"]],
    )


@pytest.fixture
def problem_entry_fixture():
    problem = ProblemEntry(
        problem_id=7,
        name="Test Problem",
        language=Language.PYTHON,
        difficulty="medium",
        short_description="Short description",
        long_description="Long description",
        template_code="def solution(): pass",
    )
    problem.tags = [ProblemTagEntry(tag="test"), ProblemTagEntry(tag="python")]
    return problem


@pytest.fixture
def problem_get_fixture():
    return ProblemDetailsResponse(
        problem_id=7,
        name="Test Problem",
        language=Language.PYTHON,
        difficulty="medium",
        tags=["test", "python"],
        short_description="Short description",
        long_description="Long description",
        template_code="def solution(): pass",
        wrappers=[["dummyname", "dummywrapper"]],
    )


@pytest.fixture
def jwt_token_data_fixture():
    return JWTokenData(
        uuid="d737eaf5-25d0-41cc-80f8-ca2adafff53a",
        username="marouan",
        permission_level=PermissionLevel.USER,
        avatar_id=0,
    )
