from uuid import uuid4

import pytest

from sqlmodel import create_engine, Session, SQLModel
from db.engine import queries
from db.engine.queries import (
    commit_entry,
    try_get_user_by_username,
    get_user_by_username,
    DBEntryNotFoundError,
)
from db.models.db_schemas import UserEntry, ProblemEntry, SubmissionEntry
from common.schemas import PermissionLevel


# --- FIXTURES ---
@pytest.fixture(name="problem_1_data")
def problem_1_data_fixture():
    return {
        "problem_id": 1,
        "name": "Two Sum",
        "tags": 3,  # Not sure how we currently handle tags!
        "description": "Find two numbers that add to target",
    }


@pytest.fixture(name="problem_1_entry")
def problem_1_entry_fixture(problem_1_data):
    return ProblemEntry(**problem_1_data)


@pytest.fixture(name="seeded_problem_1")
def seeded_problem_1_fixture(session, problem_1_data):
    problem = ProblemEntry(**problem_1_data)
    session.add(problem)
    session.commit()
    session.refresh(problem)
    return problem


@pytest.fixture(name="submission_1_data")
def submission_1_data_fixture(seeded_user_1, seeded_problem_1):
    return {
        "sid": 1,
        "problem_id": seeded_problem_1.problem_id,
        "uuid": seeded_user_1.uuid,
        "runtime_ms": 150,
        "timestamp": 1678901234,
        "successful": True,
        "score": 100,
    }


@pytest.fixture(name="seeded_submission_1")
def seeded_submission_1_fixture(session, submission_1_data):
    submission = SubmissionEntry(**submission_1_data)
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission


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


# ======================
# PROBLEM LEADERBOARD TESTS
# ======================

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


def test_get_user_by_username_not_found_fail(session):
    """Test not found user by username raises error"""
    with pytest.raises(DBEntryNotFoundError):
        queries.get_user_by_username(session, "nonexistent")


def test_get_user_by_uuid_not_found_fail(session):
    """Test not found user by UUID raises error"""
    with pytest.raises(DBEntryNotFoundError):
        queries.get_user_by_uuid(session, uuid4())


def test_get_non_existing_entry_fail(session, user_1_entry: UserEntry):
    """Test non-existing entry fails"""
    with pytest.raises(DBEntryNotFoundError):
        result = get_user_by_username(session, user_1_entry.username)


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_try_get_user_by_username_found_result(session, seeded_user_1):
    """Test found user by username"""
    user = queries.try_get_user_by_username(session, seeded_user_1.username)
    assert user is not None
    assert user.email == seeded_user_1.email


def test_try_get_user_by_username_not_found_result(session):
    """Test not found user by username"""
    user = queries.try_get_user_by_username(session, "nonexistent")
    assert user is None


def test_try_get_user_by_uuid_found_result(session, seeded_user_1):
    """Test found user by UUID"""
    user = queries.try_get_user_by_uuid(session, seeded_user_1.uuid)
    assert user is not None
    assert user.username == seeded_user_1.username


def test_try_get_user_by_uuid_not_found_result(session):
    """Test not found user by UUID"""
    user = queries.try_get_user_by_uuid(session, uuid4())
    assert user is None


def test_get_user_by_username_found_result(session, seeded_user_1):
    """Test found user by username (mandatory)"""
    user = queries.get_user_by_username(session, seeded_user_1.username)
    assert user.username == seeded_user_1.username


def test_get_user_by_uuid_found_result(session, seeded_user_1):
    """Test found user by UUID (mandatory)"""
    user = queries.get_user_by_uuid(session, seeded_user_1.uuid)
    assert user.uuid == seeded_user_1.uuid


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


# get_overall_leaderboard function not implemented yet.
# (was implemented previously on an older branch)

# def test_get_overall_leaderboard_empty_database_result(session):
#     """Test get_overall_leaderboard returns empty leaderboard for empty database"""
#     result = get_overall_leaderboard(session)
#
#     assert isinstance(result, LeaderboardGet)
#     assert result.entries == []
#
#
# def test_leaderboard_empty_when_users_but_no_submissions(session, seeded_user_1, seeded_user_2):
#     """
#     Verifies that users without any succesful submissions dont get a place on
#     the leaderboard.
#     """
#     result = get_overall_leaderboard(session)
#     assert result.entries == []
#
#
# def test_get_overall_leaderboard_with_data_result(
#     session, seeded_leaderboard_data, seeded_user_1, seeded_user_2, seeded_user_3
# ):
#     """Test get_overall_leaderboard returns correct data and ordering"""
#     result = get_overall_leaderboard(session)
#
#     # Verify return type
#     assert isinstance(result, LeaderboardGet)
#     assert len(result.entries) == 3
#
#     # Verify entries are LeaderboardEntryGet objects
#     for entry in result.entries:
#         assert isinstance(entry, LeaderboardEntryGet)
#
#     # Verify ordering (highest score first)
#     # User 1 should be first (180 total score, 2 problems)
#     # User 3 should be second (150 total score, 2 problems)
#     # User 2 should be third (90 total score, 1 problem)
#     assert result.entries[0].username == seeded_user_1.username
#     assert result.entries[0].total_score == 180
#     assert result.entries[0].problems_solved == 2
#
#     assert result.entries[1].username == seeded_user_3.username
#     assert result.entries[1].total_score == 150
#     assert result.entries[1].problems_solved == 2
#
#     assert result.entries[2].username == seeded_user_2.username
#     assert result.entries[2].total_score == 90  # Thus the unsuccessful submission is ignored
#     assert result.entries[2].problems_solved == 1


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


# def test_get_overall_leaderboard_mocker(mocker, session):
#     """
#     Test that get_overall_leaderboard:
#       * calls session.exec exactly once
#       * gets bakc rows in the form (username, total_score, problems_solved)
#       * and maps them to LeaderboardEntryGet objects in the right order
#     """
#     fake_rows = [
#         ("meneer", 42, 3),
#         ("mevrouw", 30, 2),
#     ]
#
#     mock_exec = mocker.patch.object(session, "exec")
#     fake_result = mocker.Mock()
#     fake_result.all.return_value = fake_rows
#     mock_exec.return_value = fake_result
#
#     result = get_overall_leaderboard(session)
#
#     mock_exec.assert_called_once()
#
#     assert isinstance(result, LeaderboardGet)
#     assert len(result.entries) == 2
#
#     first, second = result.entries
#     assert isinstance(first, LeaderboardEntryGet)
#     assert first.username == "meneer"
#     assert first.total_score == 42
#     assert first.problems_solved == 3
#
#     assert isinstance(second, LeaderboardEntryGet)
#     assert second.username == "mevrouw"
#     assert second.total_score == 30
#     assert second.problems_solved == 2


# ======================
# USER QUERY TESTS
# ======================

# --- CODE RESULT TESTS ---


def test_get_users_empty_result(session):
    """Test empty user list"""
    users = queries.get_users(session, offset=0, limit=10)
    assert len(users) == 0


def test_get_users_pagination_result(session):
    """Test user pagination"""
    # Create 15 users
    for i in range(1, 16):
        session.add(
            UserEntry(
                uuid=uuid4(),
                username=f"user_{i}",
                email=f"user_{i}@example.com",
                hashed_password=b"hash",
                permission_level=PermissionLevel.USER,
            )
        )
    session.commit()

    users = queries.get_users(session, offset=5, limit=5)
    assert len(users) == 5
    assert users[0].username == "user_6"
    assert users[4].username == "user_10"


def test_get_users_mocker(mocker, session):
    """Test user query construction"""
    # Mock session.exec
    mock_exec = mocker.patch.object(session, "exec")
    mock_result = mock_exec.return_value
    mock_result.all.return_value = []

    users = queries.get_users(session, offset=5, limit=5)

    mock_exec.assert_called_once()
    call = mock_exec.call_args[0][0]
    assert "OFFSET 5" in str(call)
    assert "LIMIT 5" in str(call)
    assert users == []


# ======================
# PROBLEM QUERY TESTS
# ======================

# --- CODE RESULT TESTS ---


def test_try_get_problem_found_result(session, seeded_problem_1):
    """Test found problem retrieval"""
    problem = queries.try_get_problem(session, seeded_problem_1.problem_id)
    assert problem is not None
    assert problem.name == seeded_problem_1.name


def test_try_get_problem_not_found_result(session):
    """Test not found problem retrieval"""
    problem = queries.try_get_problem(session, 9999)
    assert problem is None


def test_get_problems_empty_result(session):
    """Test empty problem list"""
    problems = queries.get_problems(session, offset=0, limit=10)
    assert len(problems) == 0


def test_get_problems_pagination_result(session):
    """Test problem pagination"""
    for i in range(1, 16):
        session.add(
            ProblemEntry(problem_id=i, name=f"Problem {i}", tags=0, description=f"Description {i}")
        )
    session.commit()

    problems = queries.get_problems(session, offset=5, limit=5)
    assert len(problems) == 5
    assert problems[0].problem_id == 6
    assert problems[4].problem_id == 10


# --- CODE FLOW TESTS ---


def test_try_get_problem_mocker(mocker, session):
    """Test problem query construction"""
    mock_exec = mocker.patch.object(session, "exec")
    mock_result = mock_exec.return_value
    mock_result.first.return_value = None

    problem = queries.try_get_problem(session, 1)

    mock_exec.assert_called_once()
    call = mock_exec.call_args[0][0]
    assert "problem_id = 1" in str(call)
    assert problem is None


def test_get_problems_mocker(mocker, session):
    """Test problems query construction"""
    mock_exec = mocker.patch.object(session, "exec")
    mock_result = mock_exec.return_value
    mock_result.all.return_value = []

    problems = queries.get_problems(session, offset=5, limit=5)

    mock_exec.assert_called_once()
    call = mock_exec.call_args[0][0]
    assert "OFFSET 5" in str(call)
    assert "LIMIT 5" in str(call)
    assert problems == []


# ======================
# SUBMISSION QUERY TESTS
# ======================

# --- CODE RESULT TESTS ---


def test_get_submissions_empty_result(session):
    """Test empty submission list"""
    submissions = queries.get_submissions(session, offset=0, limit=10)
    assert len(submissions) == 0


def test_get_submissions_pagination_result(session, seeded_problem_1, seeded_user_1):
    """Test submission pagination"""
    for i in range(1, 16):
        session.add(
            SubmissionEntry(
                sid=i,
                problem_id=seeded_problem_1.problem_id,
                uuid=seeded_user_1.uuid,
                runtime_ms=100,
                timestamp=1678900000 + i,
                successful=True,
                score=100,
            )
        )
    session.commit()

    submissions = queries.get_submissions(session, offset=5, limit=5)
    assert len(submissions) == 5
    assert submissions[0].sid == 6
    assert submissions[4].sid == 10


# --- CODE FLOW TESTS ---


def test_get_submissions_mocker(mocker, session):
    """Test submissions query construction"""
    mock_exec = mocker.patch.object(session, "exec")
    mock_result = mock_exec.return_value
    mock_result.all.return_value = []

    submissions = queries.get_submissions(session, offset=5, limit=5)

    mock_exec.assert_called_once()
    call = mock_exec.call_args[0][0]
    assert "OFFSET 5" in str(call)
    assert "LIMIT 5" in str(call)
    assert submissions == []


# ======================
# USER LOOKUP TESTS
# ======================

# --- CODE RESULT TESTS ---


def test_try_get_user_by_username_found_result(session, seeded_user_1):
    """Test found user by username"""
    user = queries.try_get_user_by_username(session, seeded_user_1.username)
    assert user is not None
    assert user.email == seeded_user_1.email


def test_try_get_user_by_username_not_found_result(session):
    """Test not found user by username"""
    user = queries.try_get_user_by_username(session, "nonexistent")
    assert user is None


def test_try_get_user_by_uuid_found_result(session, seeded_user_1):
    """Test found user by UUID"""
    user = queries.try_get_user_by_uuid(session, seeded_user_1.uuid)
    assert user is not None
    assert user.username == seeded_user_1.username


def test_try_get_user_by_uuid_not_found_result(session):
    """Test not found user by UUID"""
    user = queries.try_get_user_by_uuid(session, uuid4())
    assert user is None


def test_get_user_by_username_found_result(session, seeded_user_1):
    """Test found user by username (mandatory)"""
    user = queries.get_user_by_username(session, seeded_user_1.username)
    assert user.username == seeded_user_1.username


def test_get_user_by_uuid_found_result(session, seeded_user_1):
    """Test found user by UUID (mandatory)"""
    user = queries.get_user_by_uuid(session, seeded_user_1.uuid)
    assert user.uuid == seeded_user_1.uuid


# --- CRASH TESTS ---


def test_get_user_by_username_not_found_fail(session):
    """Test not found user by username raises error"""
    with pytest.raises(DBEntryNotFoundError):
        queries.get_user_by_username(session, "nonexistent")


def test_get_user_by_uuid_not_found_fail(session):
    """Test not found user by UUID raises error"""
    with pytest.raises(DBEntryNotFoundError):
        queries.get_user_by_uuid(session, uuid4())


# --- CODE FLOW TESTS ---


def test_try_get_user_by_username_mocker(mocker, session):
    """Test username query construction"""
    mock_exec = mocker.patch.object(session, "exec")
    mock_result = mock_exec.return_value
    mock_result.first.return_value = None

    user = queries.try_get_user_by_username(session, "testuser")

    mock_exec.assert_called_once()
    call = mock_exec.call_args[0][0]
    assert "username = 'testuser'" in str(call)
    assert user is None


def test_try_get_user_by_uuid_mocker(mocker, session):
    """Test UUID query construction"""
    test_uuid = uuid4()
    mock_exec = mocker.patch.object(session, "exec")
    mock_result = mock_exec.return_value
    mock_result.first.return_value = None

    user = queries.try_get_user_by_uuid(session, test_uuid)

    mock_exec.assert_called_once()
    call = mock_exec.call_args[0][0]
    assert f"uuid = '{test_uuid}'" in str(call)
    assert user is None


def test_get_user_by_username_mocker(mocker, session):
    """Test mandatory username query"""
    mock_exec = mocker.patch.object(session, "exec")
    mock_result = mock_exec.return_value
    mock_result.first.return_value = None

    with pytest.raises(DBEntryNotFoundError):
        queries.get_user_by_username(session, "testuser")

    mock_exec.assert_called_once()


def test_get_user_by_uuid_mocker(mocker, session):
    """Test mandatory UUID query"""
    test_uuid = uuid4()
    mock_exec = mocker.patch.object(session, "exec")
    mock_result = mock_exec.return_value
    mock_result.first.return_value = None

    with pytest.raises(DBEntryNotFoundError):
        queries.get_user_by_uuid(session, test_uuid)

    mock_exec.assert_called_once()
