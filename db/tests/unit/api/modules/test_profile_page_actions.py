from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlmodel import Session, SQLModel, create_engine

from common.auth import data_to_jwt, jwt_to_data
from common.languages import Language
from common.schemas import (
    AddProblemRequest,
    JWTokenData,
    ProblemRequest,
    RegisterRequest,
    SubmissionCreate,
    SubmissionResult,
)
from common.typing import Difficulty, PermissionLevel
from db import settings
from db.api.modules import actions

# --- FIXTURES ---


@pytest.fixture(name="session")
def session_fixture():
    """
    Provides an in-memory SQLite database session for testing.
    Tables are created and dropped for each test to ensure isolation.
    """
    # Save DB in memory
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # Clean up, good practice although probably not strictly needed here
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="user_1_register_data")
def user_1_register_data_fixture():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test_password"
    }


@pytest.fixture(name="user_1_register")
def user_1_register_fixture(user_1_register_data):
    return RegisterRequest(**user_1_register_data)


@pytest.fixture(name="problem_data_1")
def problem_data_fixture():
    return {
        "name": "C problem 1",
        "language": Language.C,
        "difficulty": Difficulty.EASY,
        "tags": ["test_tag_1", "test_tag_2"],
        "short_description": "test_short_description",
        "long_description": "test_long_description",
        "template_code": "test_template_code",
        "wrappers": [["dummyname", "dummywrapper"]],
    }


@pytest.fixture(name="problem_data_2")
def problem_data_2_fixture():
    return {
        "name": "C problem 2",
        "language": Language.C,
        "difficulty": Difficulty.HARD,
        "tags": ["test_tag_1", "test_tag_2"],
        "short_description": "test_short_description",
        "long_description": "test_long_description",
        "template_code": "test_template_code",
        "wrappers": [["dummyname", "dummywrapper"]],
    }


@pytest.fixture(name="problem_data_3")
def problem_data_3_fixture():
    return {
        "name": "Python problem 1",
        "language": Language.PYTHON,
        "difficulty": Difficulty.HARD,
        "tags": ["test_tag_1", "test_tag_2"],
        "short_description": "test_short_description",
        "long_description": "test_long_description",
        "template_code": "test_template_code",
        "wrappers": [["dummyname", "dummywrapper"]],
    }


@pytest.fixture(name="problem_request_1")
def problem_request_1_fixture(problem_data_1):
    return AddProblemRequest(**problem_data_1)


@pytest.fixture(name="problem_request_2")
def problem_request_2_fixture(problem_data_2):
    return AddProblemRequest(**problem_data_2)


@pytest.fixture(name="problem_request_3")
def problem_request_3_fixture(problem_data_3):
    return AddProblemRequest(**problem_data_3)


@pytest.fixture(name="submission_result_1")
def submission_result_1_fixture():
    return SubmissionResult(
        submission_uuid=uuid4(),
        runtime_ms=521,
        emissions_kg=2.9,
        energy_usage_kwh=0.023,
        successful=True,
        error_reason=None,
        error_msg=None,
    )


@pytest.fixture(name="submission_result_2")
def submission_result_2_fixture():
    return SubmissionResult(
        submission_uuid=uuid4(),
        runtime_ms=521,
        emissions_kg=2.9,
        energy_usage_kwh=0.023,
        successful=True,
        error_reason=None,
        error_msg=None,
    )


@pytest.fixture(name="submission_result_3")
def submission_result_3_fixture():
    return SubmissionResult(
        submission_uuid=uuid4(),
        runtime_ms=521,
        emissions_kg=2.9,
        energy_usage_kwh=0.023,
        successful=True,
        error_reason=None,
        error_msg=None,
    )


@pytest.fixture(name="admin_authorization")
def admin_authorization_fixture():
    return data_to_jwt(
        JWTokenData(
            uuid=str(uuid4()),
            username="admin",
            permission_level=PermissionLevel.ADMIN,
            avatar_id=0,
        ),
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM,
    )


@pytest.fixture(name="submission_create_1")
def submission_create_1_fixture():
    return SubmissionCreate(
        submission_uuid=uuid4(),
        problem_id=13463,
        user_uuid=uuid4(),
        language=Language.C,
        timestamp=float(datetime.now().timestamp()),
        code="test_code",
    )


@pytest.fixture(name="submission_create_2")
def submission_create_2_fixture():
    return SubmissionCreate(
        submission_uuid=uuid4(),
        problem_id=13463,
        user_uuid=uuid4(),
        language=Language.C,
        timestamp=float(datetime.now().timestamp()) + 100,
        code="test_code",
    )


@pytest.fixture(name="submission_create_3")
def submission_create_3_fixture():
    return SubmissionCreate(
        submission_uuid=uuid4(),
        problem_id=13463,
        user_uuid=uuid4(),
        language=Language.PYTHON,
        timestamp=float(datetime.now().timestamp()) + 1000,
        code="test_code",
    )


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_get_submission_result(
    session: Session,
    user_1_register: RegisterRequest,
    problem_request_1: ProblemRequest,
    problem_request_2: ProblemRequest,
    problem_request_3: ProblemRequest,
    admin_authorization: str,
    submission_create_1: SubmissionCreate,
    submission_create_2: SubmissionCreate,
    submission_create_3: SubmissionCreate,
    submission_result_1: SubmissionResult,
    submission_result_2: SubmissionResult,
    submission_result_3: SubmissionResult,
):
    token_response = actions.register_user(session, user_1_register)

    data = jwt_to_data(
        token_response.access_token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    )

    problem_1 = actions.create_problem(session, problem_request_1, admin_authorization)
    problem_2 = actions.create_problem(session, problem_request_2, admin_authorization)
    problem_3 = actions.create_problem(session, problem_request_3, admin_authorization)

    submission_create_1.user_uuid = UUID(data.uuid)
    submission_create_1.problem_id = problem_1.problem_id
    submission_result_1.submission_uuid

    submission_create_2.user_uuid = UUID(data.uuid)
    submission_create_2.problem_id = problem_2.problem_id

    submission_create_3.user_uuid = UUID(data.uuid)
    submission_create_3.problem_id = problem_3.problem_id

    submission_1 = actions.create_submission(session, submission_create_1)
    submission_2 = actions.create_submission(session, submission_create_2)
    submission_3 = actions.create_submission(session, submission_create_3)

    submission_result_1.submission_uuid = submission_1.submission_uuid
    submission_result_2.submission_uuid = submission_2.submission_uuid
    submission_result_3.submission_uuid = submission_3.submission_uuid

    actions.update_submission(session, submission_result_1)
    actions.update_submission(session, submission_result_2)
    actions.update_submission(session, submission_result_3)

    result = actions.get_profile_from_username(session, user_1_register.username)

    assert result.username == user_1_register.username
    assert result.avatar_id == 0

    assert result.solved["total"] == 3
    assert result.solved["easy"] == 1
    assert result.solved["hard"] == 2

    for language_stat in result.language_stats:
        assert language_stat["language"] in ["c", "python"]

        if language_stat["language"] == "c":
            assert language_stat["solved"] == 2
        elif language_stat["language"] == "python":
            assert language_stat["solved"] == 1

    assert result.recent_submissions[0]["title"] == "Python problem 1"
    assert result.recent_submissions[1]["title"] == "C problem 2"
    assert result.recent_submissions[2]["title"] == "C problem 1"
