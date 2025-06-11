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
    return SubmissionPost(problem_id=1, user_id="user-uuid", code="print(42)")

@pytest.fixture
def leaderboard_response():
    return LeaderboardGet(entries=[])


@patch("db.api.modules.actions.ops.register_new_user")
def test_register_user(mock_register_new_user):
    """Test that register_user calls the correct ops function and returns the expected user."""
    session = Mock()

    input = UserRegister(username="idk", password="smth")
    expected_output = UserGet(username="idk", uuid="smth-123")

    mock_register_new_user.return_value = expected_output
    result = actions.register_user(session, input)

    mock_register_new_user.assert_called_once_with(session, input)
    assert result == expected_output

k
