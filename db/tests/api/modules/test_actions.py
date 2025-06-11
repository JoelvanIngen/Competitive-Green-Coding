import pytest
from unittest.mock import Mock, patch

from db.api.modules import actions
from db.models.schemas import (
    UserRegister,
    UserLogin,
    UserGet,
    TokenResponse,
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
