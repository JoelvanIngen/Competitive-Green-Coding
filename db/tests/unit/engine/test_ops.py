from datetime import datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine

from db.engine.ops import (
    _commit_or_500,
    create_problem,
    create_submission,
    get_submissions,
    get_user_from_username,
    login_user,
    read_problem,
    read_problems,
    register_new_user,
)
from db.engine.queries import DBEntryNotFoundError
from db.models.db_schemas import UserEntry
from db.models.schemas import (
    PermissionLevel,
    ProblemGet,
    ProblemPost,
    SubmissionGet,
    SubmissionPost,
    UserGet,
    UserLogin,
    UserRegister,
)

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


@pytest.fixture(name="user_1_login")
def user_1_login_fixture(user_1_register_data):
    return UserLogin(
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
    return UserRegister(**user_2_register_data)


@pytest.fixture(name="problem_data")
def problem_data_fixture():
    return {
        "name": "test_problem",
        "language": "C",
        "difficulty": "easy",
        "tags": ["test_tag_1", "test_tag_2"],
        "short_description": "test_short_description",
        "long_description": "test_long_description",
        "template_code": "test_template_code"
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
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)

def test_commit_entry_pass(session, user_1_entry: UserEntry):
    """Test successful commit of an entry"""
    _commit_or_500(session, user_1_entry)


def test_register_user_pass(session, user_1_register: UserRegister):
    """Test successful user register"""
    register_new_user(session, user_1_register)


def test_login_user_pass(session, user_1_register: UserRegister, user_1_login: UserLogin):
    """Test successful user login"""
    register_new_user(session, user_1_register)
    login_user(session, user_1_login)


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


def test_get_submissions_pass(session):
    """Test successful retrieval of submission table"""
    get_submissions(session, 0, 100)


def test_get_user_from_username_pass(session, user_1_register: UserRegister):
    """Test successful retrieval of user with username"""
    register_new_user(session, user_1_register)
    get_user_from_username(session, user_1_register.username)


def test_read_problem_pass(session, problem_post: ProblemPost):
    """Test successful retrieval of problem with problem_id"""
    problem_get = create_problem(session, problem_post)
    read_problem(session, problem_get.problem_id)


def test_read_problems_pass(session, problem_post: ProblemPost):
    """Test successful retrieval of problem table"""
    read_problems(session, 0, 100)


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
    assert e.value.detail == "Internal server error"


def test_not_unique_username_register_fail(
    session,
    user_1_register: UserRegister,
    user_2_register: UserRegister
):
    """Test register new user with not unique username fails and raises HTTPException with status
    409"""
    register_new_user(session, user_1_register)

    with pytest.raises(HTTPException) as e:
        user_2_register.username = user_1_register.username
        register_new_user(session, user_2_register)

    assert e.value.status_code == 409
    assert e.value.detail == "PROB_USERNAME_EXISTS"


def test_not_unique_email_register_fail(
    session,
    user_1_register: UserRegister,
    user_2_register: UserRegister
):
    """Test register new user with not unique email fails and raises HTTPException with status
    409"""
    register_new_user(session, user_1_register)

    with pytest.raises(HTTPException) as e:
        user_2_register.email = user_1_register.email
        register_new_user(session, user_2_register)

    assert e.value.status_code == 409
    assert e.value.detail == "PROB_EMAIL_REGISTERED"


def test_invalid_email_register_fail(session, user_1_register: UserRegister):
    """Test register new user with invalid email fails and raises HTTPException with status
    422"""
    with pytest.raises(HTTPException) as e:
        user_1_register.email = "invalid_email"
        register_new_user(session, user_1_register)

    assert e.value.status_code == 422
    assert e.value.detail == "PROB_INVALID_EMAIL"


def test_invalid_username_register_fail(session, user_1_register: UserRegister):
    """Test register new user with invalid username fails and raises HTTPException with status
    422"""
    with pytest.raises(HTTPException) as e:
        user_1_register.username = ""
        register_new_user(session, user_1_register)

    assert e.value.status_code == 422
    assert e.value.detail == "PROB_USERNAME_CONSTRAINTS"


def test_invalid_username_login_fail(session, user_1_login: UserLogin):
    """Test username does not match constraints raises HTTPException with status 422"""
    with pytest.raises(HTTPException) as e:
        user_1_login.username = ""
        login_user(session, user_1_login)

    assert e.value.status_code == 422
    assert e.value.detail == "PROB_USERNAME_CONSTRAINTS"


def test_incorrect_password_user_login_fail(
    session,
    user_1_register: UserRegister,
    user_1_login: UserLogin
):
    """Test incorrect password raises HTTPException with status 401"""
    register_new_user(session, user_1_register)
    login_user(session, user_1_login)
    with pytest.raises(HTTPException) as e:
        user_1_login.password = "incorrect_password"
        login_user(session, user_1_login)

    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"


def test_incorrect_username_user_login_fail(
    session,
    user_1_register: UserRegister,
    user_1_login: UserLogin
):
    """Test incorrect username raises HTTPException with status 401"""
    register_new_user(session, user_1_register)
    login_user(session, user_1_login)
    with pytest.raises(HTTPException) as e:
        user_1_login.username = "IncorrectUsername"
        login_user(session, user_1_login)

    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"


def test_get_user_from_username_fail(session):
    """Test get user from username with nonexisting username raises DBEntryNotFoundError"""
    with pytest.raises(DBEntryNotFoundError):
        get_user_from_username(session, "username")


def test_read_problem_fail(session):
    """Test successful retrieval of problem with nonexisting problem_id raises HTTPException with
    status 404"""
    with pytest.raises(HTTPException) as e:
        read_problem(session, 1)

    assert e.value.status_code == 404
    assert e.value.detail == "Problem not found"


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result

def test_get_user_from_username_result(session, user_1_register: UserRegister):
    """Test retrieved user with username is correct user"""
    user_get_input = register_new_user(session, user_1_register)
    user_get_output = get_user_from_username(session, user_1_register.username)

    assert isinstance(user_get_input, UserGet)
    assert isinstance(user_get_output, UserGet)
    assert user_get_input == user_get_output


def test_user_login_result(session, user_1_register: UserRegister, user_1_login: UserLogin):
    """Test login user is correct user"""
    user_get_input = register_new_user(session, user_1_register)
    user_get_output = login_user(session, user_1_login)

    assert isinstance(user_get_input, UserGet)
    assert isinstance(user_get_output, UserGet)
    assert user_get_input == user_get_output


def test_get_submissions_result(
    session,
    submission_post: SubmissionPost,
    user_1_register: UserRegister,
    problem_post: ProblemPost
):
    """Test retrieved submission table has correct submissions"""
    user_get = register_new_user(session, user_1_register)
    problem_entry = create_problem(session, problem_post)
    submission_post.uuid = user_get.uuid
    submission_post.problem_id = problem_entry.problem_id

    submission_get = create_submission(session, submission_post)

    submissions = get_submissions(session, 0, 100)

    assert isinstance(submission_get, SubmissionGet)
    assert isinstance(submissions, list)
    assert isinstance(submissions[0], SubmissionGet)
    assert len(submissions) == 1
    assert submission_get == submissions[0]


def test_read_problem_result(session, problem_post: ProblemPost):
    """Test retrieved problem with problem_id is correct problem"""
    problem_input = create_problem(session, problem_post)
    problem_output = read_problem(session, problem_input.problem_id)

    assert isinstance(problem_input, ProblemGet)
    assert isinstance(problem_output, ProblemGet)
    assert problem_input == problem_output
    assert problem_output.tags == problem_post.tags


def test_read_problems_result(session, problem_post: ProblemPost):
    """Test retrieved problem table has correct problems"""
    problem_input = create_problem(session, problem_post)
    problems = read_problems(session, 0, 100)

    assert isinstance(problem_input, ProblemGet)
    assert isinstance(problems, list)
    assert isinstance(problems[0], ProblemGet)
    assert len(problems) == 1
    assert problem_input == problems[0]
    assert problems[0].tags == problem_post.tags


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker
