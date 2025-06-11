import pytest
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
def fake_session():
    return Mock()
    
@pytest.fixture
def sample_user_register():
    return UserRegister(username="simon", password="smthrandom")

@pytest.fixture
def sample_user_login():
    return UserLogin(username="simon", password="smthrandom")

@pytest.fixture
def expected_user_get():
    return UserGet(username="simon", uuid="123")

@pytest.fixture
def sample_problem():
    return ProblemPost(title="random", description="Do smth random")

@pytest.fixture
def sample_submission():
    return SubmissionPost(problem_id=1, user_id="1233", code="print('Hello World')")

@pytest.fixture
def leaderboard_response():
    return LeaderboardGet(entries=[])

# Tests for actions module
@patch("db.api.modules.actions.ops.register_new_user")
def test_register_user(mock_register, fake_session, sample_user_register, expected_user_get):
    """Test that register_user calls the correct ops function and returns the expected user."""
    mock_register.return_value = expected_user_get

    result = actions.register_user(fake_session, sample_user_register)

    mock_register.assert_called_once_with(fake_session, sample_user_register)
    assert result == expected_user_get

@patch("db.api.modules.actions.ops.get_user_from_username")
@patch("db.api.modules.actions.user_to_jwt")
def test_login_user(mock_user_to_jwt, mock_get_user, fake_session, sample_user_login):
    """Test that login_user retrieves the user and returns a TokenResponse."""
    mock_user = Mock()
    mock_get_user.return_value = mock_user
    mock_user_to_jwt.return_value = "fake-jwt"

    result = actions.login_user(fake_session, sample_user_login)

    mock_get_user.assert_called_once_with(fake_session, "simon")
    mock_user_to_jwt.assert_called_once_with(mock_user)
    assert isinstance(result, TokenResponse)
    assert result.access_token == "fake-jwt"


@patch("db.api.modules.actions.ops.get_user_from_username")
def test_lookup_user(mock_get_user, fake_session, expected_user_get):
    """Test that lookup_user retrieves the user by username."""
    mock_get_user.return_value = expected_user_get

    result = actions.lookup_user(fake_session, "simon")

    mock_get_user.assert_called_once_with(fake_session, "simon")
    assert result == expected_user_get


@patch("db.api.modules.actions.ops.get_leaderboard")
def test_get_leaderboard(mock_get_leaderboard, fake_session, leaderboard_response):
    """Test that get_leaderboard retrievs the leaderboard."""
    mock_get_leaderboard.return_value = leaderboard_response

    result = actions.get_leaderboard(fake_session)

    mock_get_leaderboard.assert_called_once_with(fake_session)
    assert result == leaderboard_response

@patch("db.api.modules.actions.ops.create_problem")
def test_create_problem(mock_create_problem, fake_session, sample_problem):
    """Test that create_problem actually calls ops.create_problem."""
    actions.create_problem(fake_session, sample_problem)
    mock_create_problem.assert_called_once_with(fake_session, sample_problem)

@patch("db.api.modules.actions.ops.create_submission")
def test_create_submission(mock_create_submission, fake_session, sample_submission):
    """Test that create_submission actually cals ops.create_submission."""
    actions.create_submission(fake_session, sample_submission)
    mock_create_submission.assert_called_once_with(fake_session, sample_submission)

@patch("db.api.modules.actions.ops.read_problem")
def test_read_problem(mock_read_problem, fake_session):
    """Test that read_problem actually returns the expected problem."""
    mock_problem = ProblemGet(problem_id=1, title="random", description="descrption")
    mock_read_problem.return_value = mock_problem

    result = actions.read_problem(fake_session, 1)

    mock_read_problem.assert_called_once_with(fake_session, 1)
    assert result == mock_problem
