from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine

from common.auth import data_to_jwt, jwt_to_data
from common.languages import Language
from common.schemas import (
    AddProblemRequest,
    JWTokenData,
    ProblemRequest,
    RegisterRequest,
    SubmissionCreate,
    SubmissionCreateResponse,
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


@pytest.fixture(name="problem_data")
def problem_data_fixture():
    return {
        "name": "test_problem",
        "language": Language.C,
        "difficulty": Difficulty.EASY,
        "tags": ["test_tag_1", "test_tag_2"],
        "short_description": "test_short_description",
        "long_description": "test_long_description",
        "template_code": "test_template_code",
        "wrappers": [["dummyname", "dummywrapper"]],
    }


@pytest.fixture(name="problem_request")
def problem_request_fixture(problem_data):
    return AddProblemRequest(**problem_data)


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


@pytest.fixture(name="submission_create")
def submission_create_fixture():
    return SubmissionCreate(
        submission_uuid=uuid4(),
        problem_id=13463,
        user_uuid=uuid4(),
        language=Language.C,
        timestamp=float(datetime.now().timestamp()),
        code="test_code",
    )


@pytest.fixture(name="submission_result")
def submission_result_fixture():
    return SubmissionResult(
        submission_uuid=uuid4(),
        runtime_ms=521,
        mem_usage_mb=2.9,
        energy_usage_kwh=0.023,
        successful=True,
        error_reason=None,
        error_msg=None,
    )


@pytest.fixture(name="submission_create_recent")
def submission_create_recent_fixture():
    return SubmissionCreate(
        submission_uuid=uuid4(),
        problem_id=13463,
        user_uuid=uuid4(),
        language=Language.C,
        timestamp=float(datetime.now().timestamp()) + 100,
        code="test_code_recent",
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


def test_get_submission_problem_not_found_fail(session: Session):
    with pytest.raises(HTTPException) as e:
        actions.get_submission(session, 0, uuid4())

    assert e.value.status_code == 404
    assert e.value.detail == "ERROR_PROBLEM_NOT_FOUND"


def test_get_submission_entry_not_found_fail(
    session: Session,
    problem_request: ProblemRequest,
    admin_authorization: str
):
    result = actions.create_problem(session, problem_request, admin_authorization)

    with pytest.raises(HTTPException) as e:
        actions.get_submission(session, result.problem_id, uuid4())

    assert e.value.status_code == 404
    assert e.value.detail == "ERROR_SUBMISSION_ENTRY_NOT_FOUND"


def test_get_submission_result_submission_not_found_fail(
    session: Session,
    user_1_register: RegisterRequest,
    problem_request: ProblemRequest,
    admin_authorization: str,
):
    token_response = actions.register_user(session, user_1_register)

    actions.create_problem(session, problem_request, admin_authorization)

    with pytest.raises(HTTPException) as e:
        actions.get_submission_result(
            session,
            SubmissionCreateResponse(submission_uuid=uuid4()),
            token_response.access_token,
        )

    assert e.value.status_code == 404
    assert e.value.detail == "ERROR_SUBMISSION_ENTRY_NOT_FOUND"


def test_get_submission_result_not_ready_fail(
    session: Session,
    user_1_register: RegisterRequest,
    problem_request: ProblemRequest,
    admin_authorization: str,
    submission_create: SubmissionCreate,
):
    token_response = actions.register_user(session, user_1_register)

    data = jwt_to_data(
        token_response.access_token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    )

    problem = actions.create_problem(session, problem_request, admin_authorization)

    submission_create.user_uuid = UUID(data.uuid)
    submission_create.problem_id = problem.problem_id

    submission = actions.create_submission(session, submission_create)

    with pytest.raises(HTTPException) as e:
        actions.get_submission_result(session, submission, token_response.access_token)

    assert e.value.status_code == 202
    assert e.value.detail == "SUBMISSION_NOT_READY"


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_get_submission_result(
    session: Session,
    user_1_register: RegisterRequest,
    problem_request: ProblemRequest,
    admin_authorization: str,
    submission_create: SubmissionCreate,
    submission_create_recent: SubmissionCreate
):
    token_response = actions.register_user(session, user_1_register)

    data = jwt_to_data(
        token_response.access_token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    )

    problem = actions.create_problem(session, problem_request, admin_authorization)

    submission_create.user_uuid = UUID(data.uuid)
    submission_create.problem_id = problem.problem_id

    submission_create_recent.user_uuid = UUID(data.uuid)
    submission_create_recent.problem_id = problem.problem_id

    actions.create_submission(session, submission_create)
    actions.create_submission(session, submission_create_recent)

    result = actions.get_submission(session, problem.problem_id, UUID(data.uuid))

    assert result.code == submission_create_recent.code


def test_update_submission(
    session: Session,
    user_1_register: RegisterRequest,
    problem_request: ProblemRequest,
    admin_authorization: str,
    submission_create: SubmissionCreate,
    submission_result: SubmissionResult,
):
    token_response = actions.register_user(session, user_1_register)

    data = jwt_to_data(
        token_response.access_token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    )

    problem = actions.create_problem(session, problem_request, admin_authorization)

    submission_create.user_uuid = UUID(data.uuid)
    submission_create.problem_id = problem.problem_id

    submission = actions.create_submission(session, submission_create)

    assert isinstance(submission, SubmissionCreateResponse)
    assert submission.submission_uuid == submission_create.submission_uuid

    submission_result.submission_uuid = submission.submission_uuid

    updated_submission = actions.update_submission(session, submission_result)
    assert updated_submission.submission_uuid == submission_create.submission_uuid
    assert updated_submission.runtime_ms == submission_result.runtime_ms
    assert updated_submission.user_uuid == submission_create.user_uuid


def test_get_submission_result_result(
    session: Session,
    user_1_register: RegisterRequest,
    problem_request: ProblemRequest,
    admin_authorization: str,
    submission_create: SubmissionCreate,
    submission_result: SubmissionResult,
):
    token_response = actions.register_user(session, user_1_register)

    data = jwt_to_data(
        token_response.access_token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    )

    problem = actions.create_problem(session, problem_request, admin_authorization)

    submission_create.user_uuid = UUID(data.uuid)
    submission_create.problem_id = problem.problem_id

    submission = actions.create_submission(session, submission_create)

    submission_result.submission_uuid = submission.submission_uuid

    actions.update_submission(session, submission_result)

    result = actions.get_submission_result(session, submission, token_response.access_token)

    assert submission_result == result
