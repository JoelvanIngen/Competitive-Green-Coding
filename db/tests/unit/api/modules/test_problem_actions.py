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


def test_read_problem_not_found_fail(session: Session, admin_authorization: str):
    with pytest.raises(HTTPException) as e:
        actions.read_problem(session, 0, admin_authorization)

    assert e.value.status_code == 404
    assert e.value.detail == "ERROR_PROBLEM_NOT_FOUND"


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_read_problem_result(
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
    submission_metadata = actions.create_submission(session, submission_create_recent)

    result = actions.read_problem(session, problem.problem_id, token_response.access_token)

    assert result.problem_id == problem.problem_id
    assert result.name == problem_request.name
    assert result.language == problem_request.language
    assert result.difficulty == problem_request.difficulty
    assert set(result.tags) == set(problem_request.tags)
    assert result.short_description == problem_request.short_description
    assert result.long_description == problem_request.long_description
    assert result.template_code == submission_create_recent.code
    assert result.submission_id == submission_metadata.submission_uuid
    assert result.wrappers == problem_request.wrappers
