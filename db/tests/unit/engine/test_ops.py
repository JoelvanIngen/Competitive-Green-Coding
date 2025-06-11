from typing import Optional
from uuid import uuid4

import pytest

from datetime import datetime
from fastapi import HTTPException
from sqlmodel import create_engine, Session, SQLModel, Field

from db.engine.ops import _commit_or_500, create_problem, create_submission, register_new_user
from db.engine.queries import get_users
from db.models.db_schemas import UserEntry
from db.models.schemas import PermissionLevel, ProblemPost, SubmissionPost, UserRegister
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


@pytest.fixture(name="user_1_register_data")
def user_1_register_data_fixture():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test_password"
    }


@pytest.fixture(name="user_1_register")
def user_1_register_fixture(user_1_register_data):
    return UserRegister(**user_1_register_data)


@pytest.fixture(name="user_2_register_data")
def user_2_register_data_fixture():
    return {
        "username": "anotheruser",
        "email": "another@example.com",
        "password": "test_password_2"
    }


@pytest.fixture(name="user_2_register")
def user_2_register_fixture(user_2_register_data):
    return UserRegister(**user_2_register_data)


@pytest.fixture(name="problem_data")
def problem_data_fixture():
    return {
        "name": "test_problem",
        "tags": ["C"],
        "description": "test_description"
    }


@pytest.fixture(name="problem_post")
def problem_post_fixture(problem_data):
    return ProblemPost(**problem_data)


@pytest.fixture(name="submission_data")
def submission_data_fixture():
    return {
        "problem_id": 0,
        "uuid": uuid4(),
        "runtime_ms": 100,
        "timestamp": int(datetime.now().timestamp()),
        "successful": False,
        "code": ""
    }


@pytest.fixture(name="submission_post")
def submission_post_fixture(submission_data):
    return SubmissionPost(**submission_data)


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition. Just don't write the functions around this purpose)

def test_commit_entry_pass(session, user_1_entry: UserEntry):
    """Test successful commit of an entry"""
    _commit_or_500(session, user_1_entry)


def test_register_user_pass(session, user_1_register: UserRegister):
    """Test successful user register"""
    register_new_user(session, user_1_register)


def test_create_problem_pass(session, problem_post: ProblemPost):
    """Test successful creation of submisson"""
    create_problem(session, problem_post)


def test_create_submission_pass(
    session,
    submission_post: SubmissionPost,
    user_1_register: UserRegister,
    problem_post: ProblemPost
):
    """Test successful commit of submisson"""
    user_get = register_new_user(session, user_1_register)
    problem_entry = create_problem(session, problem_post)
    submission_post.uuid = user_get.uuid
    submission_post.problem_id = problem_entry.problem_id

    create_submission(session, submission_post)


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here

def test_not_unique_username_direct_commit_fail(
    session,
    user_1_entry: UserEntry,
    user_2_entry: UserEntry
):
    """Test not unique username entry direct commit fails and raises HTTPException with status
    code 500"""
    _commit_or_500(session, user_1_entry)
    user_2_entry.username = user_1_entry.username

    with pytest.raises(HTTPException) as e:
        _commit_or_500(session, user_2_entry)

    assert e.value.status_code == 500


def test_not_unique_username_register_fail(session, user_1_register: UserRegister):
    """Test register new user with not unique username fails and raises HTTPException with status
    409"""
    register_new_user(session, user_1_register)

    with pytest.raises(HTTPException) as e:
        register_new_user(session, user_1_register)

    assert e.value.status_code == 409


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker
