import pytest
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine

from common.schemas import LoginRequest, RegisterRequest
from db.api.modules import actions

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


@pytest.fixture(name="user_1_register_data")
def user_1_register_data_fixture():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test_password"
    }


@pytest.fixture(name="user_1_register")
def user_1_register_fixture(user_1_register_data):
    return RegisterRequest(**user_1_register_data)


@pytest.fixture(name="user_1_login")
def user_1_login_fixture(user_1_register_data):
    return LoginRequest(
        username=user_1_register_data["username"],
        password=user_1_register_data["password"]
    )


@pytest.fixture(name="user_2_register_data")
def user_2_register_data_fixture():
    return {
        "username": "anotheruser",
        "email": "another@example.com",
        "password": "test_password_2"
    }


@pytest.fixture(name="user_2_register")
def user_2_register_fixture(user_2_register_data):
    return RegisterRequest(**user_2_register_data)


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


def test_not_unique_username_register_fail(
    session,
    user_1_register: RegisterRequest,
    user_2_register: RegisterRequest
):
    """Test register new user with not unique username fails and raises HTTPException with status
    409"""
    actions.register_user(session, user_1_register)

    with pytest.raises(HTTPException) as e:
        user_2_register.username = user_1_register.username
        actions.register_user(session, user_2_register)

    assert e.value.status_code == 409
    assert e.value.detail == "PROB_USERNAME_EXISTS"


def test_not_unique_email_register_fail(
    session,
    user_1_register: RegisterRequest,
    user_2_register: RegisterRequest
):
    """Test register new user with not unique email fails and raises HTTPException with status
    409"""
    actions.register_user(session, user_1_register)

    with pytest.raises(HTTPException) as e:
        user_2_register.email = user_1_register.email
        actions.register_user(session, user_2_register)

    assert e.value.status_code == 409
    assert e.value.detail == "PROB_EMAIL_REGISTERED"


def test_invalid_email_register_fail(session, user_1_register: RegisterRequest):
    """Test register new user with invalid email fails and raises HTTPException with status
    422"""
    with pytest.raises(HTTPException) as e:
        user_1_register.email = "invalid_email"
        actions.register_user(session, user_1_register)

    assert e.value.status_code == 422
    assert e.value.detail == "PROB_INVALID_EMAIL"


def test_invalid_username_register_fail(session, user_1_register: RegisterRequest):
    """Test register new user with invalid username fails and raises HTTPException with status
    422"""
    with pytest.raises(HTTPException) as e:
        user_1_register.username = ""
        actions.register_user(session, user_1_register)

    assert e.value.status_code == 422
    assert e.value.detail == "PROB_USERNAME_CONSTRAINTS"
