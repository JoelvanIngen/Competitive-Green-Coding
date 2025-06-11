import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import Mock, patch

# Importing the necessary modules and functions
from db.api.modules import actions
from db.models.schemas import (
    UserRegister,
    UserLogin,
    UserGet,
    TokenResponse,
    ProblemPost,
    SubmissionPost,
    LeaderboardGet,
    ProblemGet,
    SubmissionGet
)


# Fixtures
@pytest.fixture
def mock_session():
    return Mock()


@pytest.fixture
def sample_user_register():
    return UserRegister(username="simon", password="smthrandom", email="simon@example.com")


@pytest.fixture
def sample_user_login():
    return UserLogin(username="simon", password="smthrandom")


@pytest.fixture
def expected_user_get():
    return UserGet(username="simon", uuid=str(uuid.uuid4()), email="simon@example.com")


@pytest.fixture
def sample_problem():
    return ProblemPost(
        title="random",
        description="Do smth random",
        name="do-random",
        tags=["easy"]
    )


@pytest.fixture
def sample_submission():
    return SubmissionPost(
        problem_id=1,
        user_id="1233",
        code="print('Hello World')",
        uuid=str(uuid.uuid4()),
        runtime_ms=42,
        timestamp=int(datetime.now(timezone.utc).timestamp()),
        successful=True
    )


@pytest.fixture
def leaderboard_response():
    return LeaderboardGet(entries=[])


# Tests for actions module
@patch("db.api.modules.actions.ops.register_new_user")
def test_register_user(mock_register, mock_session, sample_user_register, expected_user_get):
    """Test that register_user calls the correct ops function and returns the expected user."""
    mock_register.return_value = expected_user_get

    result = actions.register_user(mock_session, sample_user_register)

    mock_register.assert_called_once_with(mock_session, sample_user_register)
    assert result == expected_user_get


@patch("db.api.modules.actions.ops.get_user_from_username")
@patch("db.api.modules.actions.user_to_jwt")
def test_login_user(mock_user_to_jwt, mock_get_user, mock_session, sample_user_login):
    """Test that login_user retrieves the user and returns a TokenResponse."""
    mock_user = Mock()
    mock_get_user.return_value = mock_user
    mock_user_to_jwt.return_value = "fake-jwt"

    result = actions.login_user(mock_session, sample_user_login)

    mock_get_user.assert_called_once_with(mock_session, "simon")
    mock_user_to_jwt.assert_called_once_with(mock_user)
    assert isinstance(result, TokenResponse)
    assert result.access_token == "fake-jwt"


@patch("db.api.modules.actions.ops.get_user_from_username")
def test_lookup_user(mock_get_user, mock_session, expected_user_get):
    """Test that lookup_user retrieves the user by username."""
    mock_get_user.return_value = expected_user_get

    result = actions.lookup_user(mock_session, "simon")

    mock_get_user.assert_called_once_with(mock_session, "simon")
    assert result == expected_user_get


@patch("db.api.modules.actions.ops.get_leaderboard")
def test_get_leaderboard(mock_get_leaderboard, mock_session, leaderboard_response):
    """Test that get_leaderboard retrievs the leaderboard."""
    mock_get_leaderboard.return_value = leaderboard_response

    result = actions.get_leaderboard(mock_session)

    mock_get_leaderboard.assert_called_once_with(mock_session)
    assert result == leaderboard_response


@patch("db.api.modules.actions.ops.create_problem")
def test_create_problem(mock_create_problem, mock_session, sample_problem):
    """Test that create_problem actually calls ops.create_problem."""
    actions.create_problem(mock_session, sample_problem)
    mock_create_problem.assert_called_once_with(mock_session, sample_problem)


@patch("db.api.modules.actions.ops.create_submission")
def test_create_submission(mock_create_submission, mock_session, sample_submission):
    """Test that create_submission actually cals ops.create_submission."""
    actions.create_submission(mock_session, sample_submission)
    mock_create_submission.assert_called_once_with(mock_session, sample_submission)


@patch("db.api.modules.actions.ops.read_problem")
def test_read_problem(mock_read_problem, mock_session):
    """Test that read_problem actually returns the expected problem."""
    mock_problem = ProblemGet(
        problem_id=1,
        title="random",
        description="descrption",
        name="do-random",
        tags=["easy"]
    )
    mock_read_problem.return_value = mock_problem

    result = actions.read_problem(mock_session, 1)

    mock_read_problem.assert_called_once_with(mock_session, 1)
    assert result == mock_problem


@patch("db.api.modules.actions.ops.read_problems")
def test_read_problems(mock_read_problems, mock_session):
    """Test that read_problems returns a list of problems."""
    mock_list = [ProblemGet(
        problem_id=1,
        title="problem",
        description="descripton",
        name="problem-name",
        tags=["tag122222"]
    )]
    mock_read_problems.return_value = mock_list

    result = actions.read_problems(mock_session, offset=0, limit=10)

    mock_read_problems.assert_called_once_with(mock_session, 0, 10)
    assert result == mock_list


@patch("db.api.modules.actions.ops.get_submissions")
def test_read_submissions(mock_get_submissions, mock_session):
    """Test that read_submissions returns a list of submissions."""
    mock_submissions = [SubmissionGet(
        sid=1,
        uuid=str(uuid.uuid4()),
        user_id="1",
        problem_id=1,
        code="print(1)",
        score=100,
        timestamp=int(datetime.now(timezone.utc).timestamp()),
        successful=True
    )]
    mock_get_submissions.return_value = mock_submissions

    result = actions.read_submissions(mock_session, offset=0, limit=10)

    mock_get_submissions.assert_called_once_with(mock_session, 0, 10)
    assert result == mock_submissions
