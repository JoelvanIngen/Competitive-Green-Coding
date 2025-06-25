from uuid import uuid4

import pytest
from sqlmodel import Session, SQLModel, create_engine

from common.schemas import PermissionLevel
from db.engine.queries import (
    DBEntryNotFoundError,
    commit_entry,
    get_user_by_username,
    try_get_user_by_username,
    update_user_username,
    update_user_avatar,
    update_user_private,
    delete_problem,
)
from db.models.db_schemas import UserEntry, DBCommitError

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


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition. Just don't write the functions around this purpose)


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
        result = get_user_by_username(session, user_1_entry.username)


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


def test_delete_problem_success_mocker(mocker):
    """Test that delete_problem deletes the entry and commits successfully."""
    mock_session = mocker.Mock()
    mock_problem = mocker.Mock()

    delete_problem(mock_session, mock_problem)

    mock_session.delete.assert_called_once_with(mock_problem)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()
