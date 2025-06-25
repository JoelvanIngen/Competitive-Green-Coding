from datetime import datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine

from common.languages import Language
from common.schemas import (
    AddProblemRequest,
    LoginRequest,
    PermissionLevel,
    ProblemDetailsResponse,
    RegisterRequest,
    SubmissionCreate,
    SubmissionMetadata,
    SubmissionResult,
    UserGet,
    LeaderboardRequest,
    SettingUpdateRequest,
    LeaderboardResponse,
    ProblemsListResponse,
)
from common.typing import Difficulty
from db.engine.ops import (
    _commit_or_500,
    create_problem,
    create_submission,
    get_submissions,
    get_user_from_username,
    read_problem,
    read_problems,
    register_new_user,
    try_login_user,
    update_submission,
    get_leaderboard,
    update_user_username,
    update_user_avatar,
    update_user_private,
    get_problem_metadata,
    check_unique_email,
    check_unique_username,
)
from db.engine.queries import DBEntryNotFoundError
from db.models.db_schemas import UserEntry

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
    return {"username": "testuser", "email": "test@example.com", "password": "test_password"}


@pytest.fixture(name="user_1_register")
def user_1_register_fixture(user_1_register_data):
    return RegisterRequest(**user_1_register_data)


@pytest.fixture(name="user_1_login")
def user_1_login_fixture(user_1_register_data):
    return LoginRequest(
        username=user_1_register_data["username"], password=user_1_register_data["password"]
    )


@pytest.fixture(name="user_2_register_data")
def user_2_register_data_fixture():
    return {
        "username": "anotheruser",
        "email": "another@example.com",
        "password": "test_password_2",
    }


@pytest.fixture(name="user_2_register")
def user_2_register_fixture(user_2_register_data):
    return RegisterRequest(**user_2_register_data)


@pytest.fixture(name="problem_data")
def problem_data_fixture():
    return {
        "name": "test_problem",
        "language": Language.C,
        "difficulty": Difficulty.EASY,
        "tags": ["test_tag_1", "test_tag_2"],
        "short_description": "test_short_description",
        "long_description": "test_long_description",
        "template_code": "test_template_code",
        "wrappers": [["dummyname", "dummywrapper"]],
    }


@pytest.fixture(name="problem_post")
def problem_post_fixture(problem_data):
    return AddProblemRequest(**problem_data)


@pytest.fixture(name="submission_create")
def submission_create_fixture():
    return SubmissionCreate(
        submission_uuid=uuid4(),
        problem_id=13463,
        user_uuid=uuid4(),
        language=Language.C,
        timestamp=int(datetime.now().timestamp()),
        code="test_code",
    )


@pytest.fixture(name="submission_result")
def submission_result_fixture(submission_create: SubmissionCreate):
    return SubmissionResult(
        submission_uuid=submission_create.submission_uuid,
        runtime_ms=532.21,
        mem_usage_mb=5.2,
        energy_usage_kwh=0.0,
        successful=True,
        error_reason=None,
        error_msg=None,
    )


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)


def test_update_user_avatar_pass(session, user_1_register: RegisterRequest):
    """Should persist avatar_id on the UserEntry and return it."""
    user = register_new_user(session, user_1_register)
    updated = update_user_avatar(session, user.uuid, "7")
    assert updated.avatar_id == 7
    assert session.get(UserEntry, user.uuid).avatar_id == 7


def test_update_user_private_pass(session, user_1_register: RegisterRequest):
    """Should persist private flag on the UserEntry and return it."""
    user = register_new_user(session, user_1_register)
    # default private is False
    assert session.get(UserEntry, user.uuid).private is False
    updated = update_user_private(session, user.uuid, True)
    assert updated.private is True
    assert session.get(UserEntry, user.uuid).private is True


def test_update_user_username_pass(session, user_1_register: RegisterRequest):
    """Should persist new username on the UserEntry and return it."""
    user = register_new_user(session, user_1_register)
    updated = update_user_username(session, user.uuid, "newname")
    assert updated.username == "newname"
    assert session.get(UserEntry, user.uuid).username == "newname"


def test_register_user_pass(session, user_1_register: RegisterRequest):
    """Test successful user register"""
    register_new_user(session, user_1_register)


def test_create_problem_pass(session, problem_post: AddProblemRequest):
    """Test successful creation of submission"""
    create_problem(session, problem_post)


def test_create_submission_pass(
    session,
    submission_create: SubmissionCreate,
    user_1_register: RegisterRequest,
    problem_post: AddProblemRequest,
):
    """Test successful commit of submission"""
    user_get = register_new_user(session, user_1_register)
    problem_entry = create_problem(session, problem_post)
    submission_create.user_uuid = user_get.uuid
    submission_create.problem_id = problem_entry.problem_id

    create_submission(session, submission_create)


def test_get_submissions_pass(session):
    """Test successful retrieval of submission table"""
    get_submissions(session, 0, 100)


def test_get_user_from_username_pass(session, user_1_register: RegisterRequest):
    """Test successful retrieval of user with username"""
    register_new_user(session, user_1_register)
    get_user_from_username(session, user_1_register.username)


def test_read_problem_pass(session, problem_post: AddProblemRequest):
    """Test successful retrieval of problem with problem_id"""
    problem_get = create_problem(session, problem_post)
    read_problem(session, problem_get.problem_id)


def test_read_problems_pass(session, problem_post: AddProblemRequest):
    """Test successful retrieval of problem table"""
    read_problems(session, 0, 100)


def test_check_unique_username_pass(session: Session, user_1_register: RegisterRequest):
    check_unique_username(session, user_1_register.username)


def test_check_unique_email_pass(session: Session, user_1_register: RegisterRequest):
    check_unique_email(session, user_1_register.email)


def test_try_login_pass(session: Session, user_1_login: LoginRequest):
    try_login_user(session, user_1_login)


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


def test_update_user_avatar_not_found_fail(session):
    """CRASH TEST: updating avatar for nonexistent user should raise DBEntryNotFoundError"""
    nonexistent_uuid = uuid4()
    with pytest.raises(DBEntryNotFoundError):
        update_user_avatar(session, nonexistent_uuid, "1")


def test_update_user_private_not_found_fail(session):
    """CRASH TEST: updating privacy for nonexistent user should raise DBEntryNotFoundError"""
    nonexistent_uuid = uuid4()
    with pytest.raises(DBEntryNotFoundError):
        update_user_private(session, nonexistent_uuid, True)


def test_update_user_username_not_found_fail(session):
    """CRASH TEST: updating username for nonexistent user should raise DBEntryNotFoundError"""
    nonexistent_uuid = uuid4()
    with pytest.raises(DBEntryNotFoundError):
        update_user_username(session, nonexistent_uuid, "newname")


def test_not_unique_username_direct_commit_fail(
    session, user_1_entry: UserEntry, user_2_entry: UserEntry
):
    """Test not unique username entry direct commit fails and raises HTTPException with status
    code 500"""
    _commit_or_500(session, user_1_entry)
    user_2_entry.username = user_1_entry.username

    with pytest.raises(HTTPException) as e:
        _commit_or_500(session, user_2_entry)

    assert e.value.status_code == 500
    assert e.value.detail == "Internal server error"


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


def test_get_leaderboard_no_problem_fail(session):
    """test_get_leaderboard_no_problem_fail: requesting a non-existent problem raises
    DBEntryNotFoundError"""
    with pytest.raises(DBEntryNotFoundError):
        get_leaderboard(
            session,
            LeaderboardRequest(problem_id=9999, first_row=0, last_row=10),
        )


def test_update_user_username_ops_not_found_fail(session):
    with pytest.raises(DBEntryNotFoundError):
        update_user_username(session, uuid4(), "newname")


def test_update_user_avatar_ops_not_found_fail(session):
    with pytest.raises(DBEntryNotFoundError):
        update_user_avatar(session, uuid4(), 7)


def test_update_user_private_ops_not_found_fail(session):
    with pytest.raises(DBEntryNotFoundError):
        update_user_private(session, uuid4(), True)


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_get_leaderboard_result(session):
    """test_get_leaderboard_result: should return scores ordered by least energy."""
    pwd = "password123"

    u1 = register_new_user(
        session,
        RegisterRequest(username="groot", email="groot@galaxy.com", password=pwd),
    )
    u2 = register_new_user(
        session,
        RegisterRequest(username="tom", email="tom@gone.com", password=pwd),
    )

    prob = create_problem(
        session,
        AddProblemRequest(
            name="sum",
            language=Language.C,
            difficulty=Difficulty.EASY,
            tags=[],
            short_description="",
            long_description="",
            template_code="",
            wrappers=[["dummyname", ""]],
        ),
    )

    for energy in (10.0, 5.0):
        sub = SubmissionCreate(
            submission_uuid=uuid4(),
            problem_id=prob.problem_id,
            user_uuid=u1.uuid,
            language=Language.C,
            timestamp=int(datetime.now().timestamp()),
            code="code",
        )
        create_submission(session, sub)
        update_submission(
            session,
            SubmissionResult(
                submission_uuid=sub.submission_uuid,
                runtime_ms=0.0,
                mem_usage_mb=0.0,
                energy_usage_kwh=energy,
                successful=True,
                error_reason=None,
                error_msg=None,
            ),
        )

    sub = SubmissionCreate(
        submission_uuid=uuid4(),
        problem_id=prob.problem_id,
        user_uuid=u2.uuid,
        language=Language.C,
        timestamp=int(datetime.now().timestamp()),
        code="code",
    )
    create_submission(session, sub)
    update_submission(
        session,
        SubmissionResult(
            submission_uuid=sub.submission_uuid,
            runtime_ms=0.0,
            mem_usage_mb=0.0,
            energy_usage_kwh=20.0,
            successful=True,
            error_reason=None,
            error_msg=None,
        ),
    )

    lb = get_leaderboard(
        session,
        LeaderboardRequest(problem_id=prob.problem_id, first_row=0, last_row=10),
    )
    usernames = [s.username for s in lb.scores]
    energies = [s.score for s in lb.scores]

    assert usernames == ["groot", "tom"]
    assert energies == [pytest.approx(5.0), pytest.approx(20.0)]


def test_get_user_from_username_result(session, user_1_register: RegisterRequest):
    """Test retrieved user with username is correct user"""
    user_get_input = register_new_user(session, user_1_register)
    user_get_output = get_user_from_username(session, user_1_register.username)

    assert isinstance(user_get_input, UserGet)
    assert isinstance(user_get_output, UserGet)
    assert user_get_input == user_get_output


def test_get_submissions_result(
    session,
    submission_create: SubmissionCreate,
    submission_result: SubmissionResult,
    user_1_register: RegisterRequest,
    problem_post: AddProblemRequest,
):
    """Test retrieved submission table has correct submissions"""
    user_get = register_new_user(session, user_1_register)
    problem_entry = create_problem(session, problem_post)
    submission_create.user_uuid = user_get.uuid
    submission_create.problem_id = problem_entry.problem_id

    submission_metadata = create_submission(session, submission_create)
    update_submission(session, submission_result)

    submissions = get_submissions(session, 0, 100)

    assert isinstance(submission_metadata, SubmissionMetadata)
    assert isinstance(submissions, list)
    assert isinstance(submissions[0], SubmissionMetadata)
    assert len(submissions) == 1


def test_read_problem_result(session, problem_post: AddProblemRequest):
    """Test retrieved problem with problem_id is correct problem"""
    problem_input = create_problem(session, problem_post)
    problem_output = read_problem(session, problem_input.problem_id)

    assert isinstance(problem_input, ProblemDetailsResponse)
    assert isinstance(problem_output, ProblemDetailsResponse)
    assert problem_input == problem_output
    assert problem_output.tags == problem_post.tags


def test_read_problems_result(session, problem_post: AddProblemRequest):
    """Test retrieved problem table has correct problems"""
    problem_input = create_problem(session, problem_post)
    problems = read_problems(session, 0, 100)

    assert isinstance(problem_input, ProblemDetailsResponse)
    assert isinstance(problems, list)
    assert isinstance(problems[0], ProblemDetailsResponse)
    assert len(problems) == 1
    assert problem_input == problems[0]
    assert problems[0].tags == problem_post.tags


def test_check_unique_username_result(
    session: Session, user_1_register: RegisterRequest, user_2_register: RegisterRequest
):
    assert check_unique_username(session, user_1_register.username) is True

    register_new_user(session, user_1_register)

    assert check_unique_username(session, user_1_register.username) is False
    assert check_unique_username(session, user_2_register.username) is True


def test_check_unique_email_result(
    session: Session, user_1_register: RegisterRequest, user_2_register: RegisterRequest
):
    assert check_unique_email(session, user_1_register.email) is True

    register_new_user(session, user_1_register)

    assert check_unique_email(session, user_1_register.email) is False
    assert check_unique_email(session, user_2_register.email) is True


def test_get_problem_metadata_result(session, problem_post: AddProblemRequest):
    """Test that get_problem_metadata returns ProblemMetadata items in ProblemsListResponse"""
    create_problem(session, problem_post)

    result = get_problem_metadata(session, offset=0, limit=10)

    assert isinstance(result, ProblemsListResponse)
    assert result.total == 1
    assert len(result.problems) == 1
    summary = result.problems[0]
    assert summary.name == problem_post.name
    assert summary.difficulty == problem_post.difficulty
    assert summary.short_description == problem_post.short_description


def test_try_login_result(
    session: Session, user_1_register: RegisterRequest, user_1_login: LoginRequest
):
    user_get = try_login_user(session, user_1_login)

    assert user_get is None

    user_get_input = register_new_user(session, user_1_register)
    user_get_output = try_login_user(session, user_1_login)

    assert user_get_input == user_get_output


def test_get_leaderboard_success(session):
    """Alternative success test, asserting the returned object type and fields."""
    pwd = "password123"

    reg1 = RegisterRequest(username="groot", email="groot@galaxy.com", password=pwd)
    u1 = register_new_user(session, reg1)
    reg2 = RegisterRequest(username="tom", email="tom@gone.com", password=pwd)
    u2 = register_new_user(session, reg2)
    reg3 = RegisterRequest(username="olaf", email="olaf@gmail.com", password=pwd)
    u3 = register_new_user(session, reg3)

    prob = create_problem(
        session,
        AddProblemRequest(
            name="sum",
            language=Language.C,
            difficulty=Difficulty.EASY,
            tags=[],
            short_description="",
            long_description="",
            template_code="",
            wrappers=[["dummyname", ""]],
        ),
    )

    for energy in (10.0, 5.0):
        sub = SubmissionCreate(
            submission_uuid=uuid4(),
            problem_id=prob.problem_id,
            user_uuid=u1.uuid,
            language=Language.C,
            timestamp=int(datetime.now().timestamp()),
            code="print('hi')",
        )
        create_submission(session, sub)
        update_submission(
            session,
            SubmissionResult(
                submission_uuid=sub.submission_uuid,
                runtime_ms=100.0,
                mem_usage_mb=0.0,
                energy_usage_kwh=energy,
                successful=True,
                error_reason=None,
                error_msg=None,
            ),
        )

    sub = SubmissionCreate(
        submission_uuid=uuid4(),
        problem_id=prob.problem_id,
        user_uuid=u2.uuid,
        language=Language.C,
        timestamp=int(datetime.now().timestamp()),
        code="print('hey')",
    )
    create_submission(session, sub)
    update_submission(
        session,
        SubmissionResult(
            submission_uuid=sub.submission_uuid,
            runtime_ms=200.0,
            mem_usage_mb=0.0,
            energy_usage_kwh=20.0,
            successful=True,
            error_reason=None,
            error_msg=None,
        ),
    )

    sub = SubmissionCreate(
        submission_uuid=uuid4(),
        problem_id=prob.problem_id,
        user_uuid=u3.uuid,
        language=Language.C,
        timestamp=int(datetime.now().timestamp()),
        code="print('o')",
    )
    create_submission(session, sub)
    update_submission(
        session,
        SubmissionResult(
            submission_uuid=sub.submission_uuid,
            runtime_ms=50.0,
            mem_usage_mb=0.0,
            energy_usage_kwh=1.0,
            successful=True,
            error_reason=None,
            error_msg=None,
        ),
    )

    update_user_private(session, u3.uuid, True)

    lb = get_leaderboard(
        session,
        LeaderboardRequest(problem_id=prob.problem_id, first_row=0, last_row=10),
    )
    assert isinstance(lb, LeaderboardResponse)
    assert lb.problem_id == prob.problem_id

    usernames = [sc.username for sc in lb.scores]
    energies = [sc.score for sc in lb.scores]
    assert usernames == ["groot", "tom"]
    assert energies == [pytest.approx(5.0), pytest.approx(20.0)]


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker
