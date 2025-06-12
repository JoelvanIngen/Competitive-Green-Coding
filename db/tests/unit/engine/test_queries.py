from typing import Optional
from uuid import uuid4

import pytest

from sqlmodel import create_engine, Session, SQLModel, Field

from db.engine.queries import commit_entry, try_get_user_by_username, DBEntryNotFoundError, get_user_by_username
from db.models.db_schemas import UserEntry
from db.models.schemas import PermissionLevel
from db.typing import DBEntry


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


def test_get_overall_leaderboard_empty_database_result(session):
    """Test get_overall_leaderboard returns empty leaderboard for empty database"""
    result = get_overall_leaderboard(session)

    assert isinstance(result, LeaderboardGet)
    assert result.entries == []


def test_leaderboard_empty_when_users_but_no_submissions(session, seeded_user_1, seeded_user_2):
    """
    Verifies that users without any succesful submissions dont get a place on
    the leaderboard.
    """
    result = get_overall_leaderboard(session)
    assert result.entries == []


def test_get_overall_leaderboard_with_data_result(session, seeded_leaderboard_data, seeded_user_1, seeded_user_2, seeded_user_3):
    """Test get_overall_leaderboard returns correct data and ordering"""
    result = get_overall_leaderboard(session)

    # Verify return type
    assert isinstance(result, LeaderboardGet)
    assert len(result.entries) == 3

    # Verify entries are LeaderboardEntryGet objects
    for entry in result.entries:
        assert isinstance(entry, LeaderboardEntryGet)

    # Verify ordering (highest score first)
    # User 1 should be first (180 total score, 2 problems)
    # User 3 should be second (150 total score, 2 problems)
    # User 2 should be third (90 total score, 1 problem)
    assert result.entries[0].username == seeded_user_1.username
    assert result.entries[0].total_score == 180
    assert result.entries[0].problems_solved == 2

    assert result.entries[1].username == seeded_user_3.username
    assert result.entries[1].total_score == 150
    assert result.entries[1].problems_solved == 2

    assert result.entries[2].username == seeded_user_2.username
    assert result.entries[2].total_score == 90 # Thus the unsuccessful submission is ignored
    assert result.entries[2].problems_solved == 1


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


def test_get_overall_leaderboard_mocker(mocker, session):
    """
    Test that get_overall_leaderboard:
      * calls session.exec exactly once
      * gets bakc rows in the form (username, total_score, problems_solved)
      * and maps them to LeaderboardEntryGet objects in the right order
    """
    fake_rows = [
        ("meneer", 42, 3),
        ("mevrouw", 30, 2),
    ]

    mock_exec = mocker.patch.object(session, "exec")
    fake_result = mocker.Mock()
    fake_result.all.return_value = fake_rows
    mock_exec.return_value = fake_result

    result = get_overall_leaderboard(session)

    mock_exec.assert_called_once()

    assert isinstance(result, LeaderboardGet)
    assert len(result.entries) == 2

    first, second = result.entries
    assert isinstance(first, LeaderboardEntryGet)
    assert first.username == "meneer"
    assert first.total_score == 42
    assert first.problems_solved == 3

    assert isinstance(second, LeaderboardEntryGet)
    assert second.username == "mevrouw"
    assert second.total_score == 30
    assert second.problems_solved == 2
