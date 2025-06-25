from datetime import datetime
from uuid import uuid4

import pytest
from sqlmodel import Session, SQLModel, create_engine

from common.languages import Language
from common.schemas import Difficulty, PermissionLevel
from db.engine.queries import (
    DBEntryNotFoundError,
    commit_entry,
    get_submission_from_problem_user_ids,
    get_user_by_username,
    try_get_user_by_username,
    update_user_avatar,
    update_user_private,
    update_user_username,
    delete_entry,
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
        "energy_usage_kwh": 100,
        "timestamp": float(datetime.now().timestamp()),
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
        "energy_usage_kwh": 100,
        "timestamp": float(datetime.now().timestamp()),
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


def test_update_user_avatar_pass(session, seeded_user_1):
    """Should update avatar_id on the seeded entry."""
    updated = update_user_avatar(session, seeded_user_1, 9)
    assert updated.avatar_id == 9
    assert session.get(UserEntry, seeded_user_1.uuid).avatar_id == 9


def test_update_user_private_pass(session, seeded_user_1):
    """Should update private flag on the seeded entry."""
    updated = update_user_private(session, seeded_user_1, True)
    assert updated.private is True
    assert session.get(UserEntry, seeded_user_1.uuid).private is True


def test_update_user_username_pass(session, seeded_user_1):
    """Should update username on the seeded entry."""
    updated = update_user_username(session, seeded_user_1, "brandnew")
    assert updated.username == "brandnew"
    assert session.get(UserEntry, seeded_user_1.uuid).username == "brandnew"


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


def test_get_non_existing_entry_fail(session, user_1_entry: UserEntry):
    """Test non-existing entry fails"""
    with pytest.raises(DBEntryNotFoundError):
        get_user_by_username(session, user_1_entry.username)


def test_get_submission_from_problem_user_ids_fail(
    session, user_1_entry: UserEntry, problem_data: dict
):
    """Test non-existing submission fails"""

    with pytest.raises(DBEntryNotFoundError):
        get_submission_from_problem_user_ids(session, problem_data["problem_id"], user_1_entry.uuid)


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


def test_get_submission_from_problem_user_ids_result(
    session,
    user_1_entry: UserEntry,
    user_2_entry: UserEntry,
    problem_data: dict,
    user_1_submission_data: dict,
    user_2_submission_data: dict,
):
    """Test successful retrieval of most recent submission"""

    commit_entry(session, user_1_entry)
    commit_entry(session, user_2_entry)

    commit_entry(session, ProblemEntry(**problem_data))

    commit_entry(session, SubmissionEntry(**user_1_submission_data))
    commit_entry(session, SubmissionEntry(**user_2_submission_data))

    user_1_submission_data["timestamp"] = float(datetime.now().timestamp())
    user_1_submission_data["energy_usage_kwh"] = 10
    commit_entry(session, SubmissionEntry(**user_1_submission_data))

    user_1_submission_data["timestamp"] = float(datetime.now().timestamp())
    user_1_submission_data["energy_usage_kwh"] = 50
    commit_entry(session, SubmissionEntry(**user_1_submission_data))
    most_recent = user_1_submission_data.copy()

    problem_data["problem_id"] = 1
    commit_entry(session, ProblemEntry(**problem_data))

    user_1_submission_data["timestamp"] = float(datetime.now().timestamp())
    user_1_submission_data["problem_id"] = 1
    user_1_submission_data["energy_usage_kwh"] = 40
    commit_entry(session, SubmissionEntry(**user_1_submission_data))

    result = get_submission_from_problem_user_ids(session, 0, user_1_submission_data["user_uuid"])

    assert result.problem_id == 0
    assert result.user_uuid == most_recent["user_uuid"]
    assert result.language == most_recent["language"]
    assert result.runtime_ms == most_recent["runtime_ms"]
    assert result.mem_usage_mb == most_recent["mem_usage_mb"]
    assert result.energy_usage_kwh == most_recent["energy_usage_kwh"]
    assert result.timestamp == most_recent["timestamp"]
    assert result.executed == most_recent["executed"]
    assert result.successful == most_recent["successful"]
    assert result.error_reason == most_recent["error_reason"]
    assert result.error_msg == most_recent["error_msg"]


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker


def test_commit_entry_success_mocker(mocker, user_1_entry, session):
    """
    Test that commit_entry correctly adds, commits, and refreshes an entry
    when no errors occur.
    """
    # Stalk session methods so we can track how they were used
    mock_add = mocker.patch.object(session, "add")
    mock_commit = mocker.patch.object(session, "commit")
    mock_refresh = mocker.patch.object(session, "refresh")
    mock_rollback = mocker.patch.object(session, "rollback")

    commit_entry(session, user_1_entry)

    # Assert that the methods were called as expected
    mock_add.assert_called_once_with(user_1_entry)
    mock_commit.assert_called_once()
    mock_refresh.assert_called_once_with(user_1_entry)
    mock_rollback.assert_not_called()
