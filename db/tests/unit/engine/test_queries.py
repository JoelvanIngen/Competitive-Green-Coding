from datetime import datetime
from uuid import uuid4

import pytest
from sqlmodel import Session, SQLModel, create_engine

from common.languages import Language
from common.schemas import PermissionLevel
from common.typing import Difficulty
from db.engine.queries import (
    DBEntryNotFoundError,
    commit_entry,
    get_user_by_username,
    try_get_user_by_username,
    get_solved_submissions_by_difficulty,
)
from db.models.db_schemas import ProblemEntry, SubmissionEntry, UserEntry

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


@pytest.fixture(name="user_1_data")
def user_1_data_fixture():
    return {
        "uuid": uuid4(),
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": b"test_hashed",
        "permission_level": PermissionLevel.USER,
    }


@pytest.fixture(name="user_1_entry")
def user_1_entry_fixture(user_1_data):
    return UserEntry(**user_1_data)


@pytest.fixture(name="user_2_data")
def user_2_data_fixture():
    return {
        "uuid": uuid4(),
        "username": "anotheruser",
        "email": "another@example.com",
        "hashed_password": b"Banaan1!",
        "permission_level": PermissionLevel.USER,
    }


@pytest.fixture(name="user_2_entry")
def user_2_entry_fixture(user_2_data):
    return UserEntry(**user_2_data)


@pytest.fixture(name="seeded_user_1")
def seeded_user_1_fixture(session, user_1_data: dict):
    """
    Creates and commits a user to the database for tests that require existing data.
    """
    user = UserEntry(**user_1_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="seeded_user_2")
def seeded_user_2_fixture(session, user_2_data: dict):
    """
    Creates and commits a second user to the database.
    """
    user = UserEntry(**user_2_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="problem_data")
def problem_data_fixture():
    return {
        "problem_id": 0,
        "name": "test_problem",
        "language": Language.C,
        "difficulty": Difficulty.EASY,
        "short_description": "",
        "long_description": "",
        "template_code": ""
    }


@pytest.fixture(name="user_1_submission_data")
def user_1_submission_data_fixture(user_1_entry):
    return {
        "problem_id": 0,
        "user_uuid": user_1_entry.uuid,
        "language": Language.C,
        "runtime_ms": 0,
        "mem_usage_mb": 0,
        "energy_usage_kwh": 0,
        "timestamp": int(datetime.now().timestamp()),
        "executed": True,
        "successful": True,
        "error_reason": None,
        "error_msg": None,
    }


@pytest.fixture(name="user_2_submission_data")
def user_2_submission_data_fixture(user_2_entry):
    return {
        "problem_id": 0,
        "user_uuid": user_2_entry.uuid,
        "language": Language.C,
        "runtime_ms": 0,
        "mem_usage_mb": 0,
        "energy_usage_kwh": 0,
        "timestamp": int(datetime.now().timestamp()),
        "executed": True,
        "successful": True,
        "error_reason": None,
        "error_msg": None,
    }


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
# Just don't write the functions around this purpose)

def test_commit_entry_pass(session, user_1_entry: UserEntry):
    """Test successful commit of an entry"""
    commit_entry(session, user_1_entry)


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here

def test_get_non_existing_entry_fail(session, user_1_entry: UserEntry):
    """Test non-existing entry fails"""
    with pytest.raises(DBEntryNotFoundError):
        _ = get_user_by_username(session, user_1_entry.username)


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result

def test_commit_entry_success_result(session, user_1_entry: UserEntry):
    """Test successful commit and retrieval of an entry"""
    username = user_1_entry.username
    email = user_1_entry.email

    commit_entry(session, user_1_entry)

    # Verify the user was committed
    result = try_get_user_by_username(session, username)
    assert result is not None
    assert result.username == username
    assert result.email == email


def test_get_solved_submissions_by_difficulty_result(
    session: Session,
    user_1_entry: UserEntry,
    user_2_entry: UserEntry,
    problem_data: dict,
    user_1_submission_data: dict,
    user_2_submission_data: dict,
):
    commit_entry(session, user_1_entry)
    commit_entry(session, user_2_entry)

    commit_entry(session, ProblemEntry(**problem_data))

    user_1_submission_data["problem_id"] = problem_data["problem_id"]
    user_2_submission_data["problem_id"] = problem_data["problem_id"]
    commit_entry(session, SubmissionEntry(**user_1_submission_data))
    commit_entry(session, SubmissionEntry(**user_1_submission_data))
    commit_entry(session, SubmissionEntry(**user_2_submission_data))

    user_1_submission_data["successful"] = False
    user_2_submission_data["successful"] = False
    commit_entry(session, SubmissionEntry(**user_1_submission_data))
    commit_entry(session, SubmissionEntry(**user_2_submission_data))

    problem_data["difficulty"] = Difficulty.MEDIUM
    problem_data["problem_id"] = 1
    commit_entry(session, ProblemEntry(**problem_data))

    user_1_submission_data["problem_id"] = problem_data["problem_id"]
    user_2_submission_data["problem_id"] = problem_data["problem_id"]
    commit_entry(session, SubmissionEntry(**user_1_submission_data))
    commit_entry(session, SubmissionEntry(**user_2_submission_data))

    problem_data["difficulty"] = Difficulty.HARD
    problem_data["problem_id"] = 2
    commit_entry(session, ProblemEntry(**problem_data))

    user_1_submission_data["problem_id"] = problem_data["problem_id"]
    user_2_submission_data["problem_id"] = problem_data["problem_id"]
    user_1_submission_data["successful"] = True
    user_2_submission_data["successful"] = True
    commit_entry(session, SubmissionEntry(**user_1_submission_data))
    commit_entry(session, SubmissionEntry(**user_2_submission_data))

    problem_data["problem_id"] = 3
    commit_entry(session, ProblemEntry(**problem_data))

    user_1_submission_data["problem_id"] = problem_data["problem_id"]
    user_2_submission_data["problem_id"] = problem_data["problem_id"]
    user_2_submission_data["successful"] = False
    commit_entry(session, SubmissionEntry(**user_1_submission_data))
    commit_entry(session, SubmissionEntry(**user_2_submission_data))

    assert get_solved_submissions_by_difficulty(session, user_1_entry.uuid, Difficulty.EASY) == 1
    assert get_solved_submissions_by_difficulty(session, user_2_entry.uuid, Difficulty.EASY) == 1

    assert get_solved_submissions_by_difficulty(session, user_1_entry.uuid, Difficulty.MEDIUM) == 0
    assert get_solved_submissions_by_difficulty(session, user_2_entry.uuid, Difficulty.MEDIUM) == 0

    assert get_solved_submissions_by_difficulty(session, user_1_entry.uuid, Difficulty.HARD) == 2
    assert get_solved_submissions_by_difficulty(session, user_2_entry.uuid, Difficulty.HARD) == 1


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker

def test_commit_entry_success_mocker(mocker, user_1_entry, session):
    """
    Test that commit_entry correctly adds, commits, and refreshes an entry
    when no errors occur.
    """
    # Stalk session methods so we can track how they were used
    mock_add = mocker.patch.object(session, 'add')
    mock_commit = mocker.patch.object(session, 'commit')
    mock_refresh = mocker.patch.object(session, 'refresh')
    mock_rollback = mocker.patch.object(session, 'rollback')

    commit_entry(session, user_1_entry)

    # Assert that the methods were called as expected
    mock_add.assert_called_once_with(user_1_entry)
    mock_commit.assert_called_once()
    mock_refresh.assert_called_once_with(user_1_entry)
    mock_rollback.assert_not_called()
