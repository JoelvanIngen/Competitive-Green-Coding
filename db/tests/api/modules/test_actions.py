import pytest
from unittest.mock import Mock, patch

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


@patch("db.api.modules.actions.ops.register_new_user")
def test_register_user(mock_register, fake_session, sample_user_register, expected_user_get):
    """Test that register_user calls the correct ops function and returns the expected user."""
    mock_register.return_value = expected_user_get
    result = actions.register_user(fake_session, sample_user_register)
    mock_register.assert_called_once_with(fake_session, sample_user_register)
    assert result == expected_user_get

