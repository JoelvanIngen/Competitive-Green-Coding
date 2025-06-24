import uuid
from datetime import timedelta

import pytest
from fastapi import HTTPException
from pytest_mock import MockerFixture
from sqlmodel import Session, SQLModel, create_engine

from common.auth import hash_password, jwt_to_data, data_to_jwt
from common.languages import Language
from common.schemas import (
    AddProblemRequest,
    JWTokenData,
    LoginRequest,
    PermissionLevel,
    ProblemDetailsResponse,
    RegisterRequest,
    SubmissionCreate,
    SubmissionFull,
    TokenResponse,
    UserGet,
    LeaderboardRequest,
    LeaderboardResponse,
    UserScore,
    ProblemsListResponse,
    ProblemMetadata,
)
from common.typing import Difficulty
from db import settings
from db.api.modules import actions
from db.models.db_schemas import UserEntry


# Fixtures
@pytest.fixture(name="session")
def mock_session_fixture(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture(name="login_session")
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
    return {"username": "testuser", "email": "test@example.com", "password": "test_password"}


@pytest.fixture(name="user_1_register")
def user_1_register_fixture(user_1_register_data):
    return RegisterRequest(**user_1_register_data)


@pytest.fixture(name="user_1_login")
def user_1_login_fixture(user_1_register_data):
    return LoginRequest(
        username=user_1_register_data["username"], password=user_1_register_data["password"]
    )


@pytest.fixture(name="user_register")
def user_register_fixture():
    return RegisterRequest(username="simon", password="smthrandom", email="simon@example.com")


@pytest.fixture(name="user_login")
def user_login_fixture():
    return LoginRequest(username="simon", password="smthrandom")


@pytest.fixture(name="user_get")
def user_get_fixture():
    return UserGet(username="simon", uuid=uuid.uuid4(), email="simon@example.com")


@pytest.fixture(name="problem_data")
def problem_data_fixture():
    return {
        "name": "test_problem",
        "language": "C",
        "difficulty": "easy",
        "tags": ["test_tag_1", "test_tag_2"],
        "short_description": "test_short_description",
        "long_description": "test_long_description",
        "template_code": "test_template_code",
    }


@pytest.fixture(name="problem_request")
def problem_request_fixture():
    return AddProblemRequest(
        name="dijkstra",
        language=Language.PYTHON,
        difficulty=Difficulty.EASY,
        tags=["graph", "algorithm"],
        short_description="short_description",
        long_description="long_description",
        template_code="SF6",
        wrappers=[["dummyname", "dummycontent"]]
    )


@pytest.fixture(name="faulty_problem_request")
def faulty_problem_request_fixture():
    return AddProblemRequest(
        name="quicksort",
        language=Language.PYTHON,
        difficulty=Difficulty.EASY,
        tags=["graph", "algorithm"],
        short_description="short_description",
        long_description="long_description",
        template_code="MK1",
        wrappers=[["dummyname", "dummycontent"]]
    )


@pytest.fixture(name="timestamp")
def timestamp_fixture() -> int:
    return 1678886400


@pytest.fixture(name="submission_post")
def submission_create_fixture(timestamp: int):
    return SubmissionCreate(
        submission_uuid=uuid.uuid4(),
        problem_id=1,
        user_uuid=uuid.uuid4(),
        language=Language.C,
        timestamp=timestamp,
        code="print('Hello World')",
    )


@pytest.fixture(name="board_request")
def board_request_fixture():
    return LeaderboardRequest(problem_id=1, first_row=0, last_row=10)


@pytest.fixture(name="fake_leaderboard")
def fake_leaderboard_fixture():
    return LeaderboardResponse(
        problem_id=1,
        problem_name="demo",
        problem_language=Language.PYTHON,
        problem_difficulty=Difficulty.EASY,
        scores=[UserScore(username="groot", score=5.0)],
    )


@pytest.fixture(name="mock_problem_get")
def mock_problem_get_fixture():
    return ProblemDetailsResponse(
        problem_id=1,
        name="do-random",
        language=Language.PYTHON,
        difficulty=Difficulty.EASY,
        tags=["tag1", "tag2"],
        short_description="A python problem",
        long_description="Python problem very long description",
        template_code="def main(): ...",
        wrappers=[["dummmyname", "dummywrapper"]]
    )


@pytest.fixture(name="mock_submission_get")
def mock_submission_get_fixture(timestamp: int):
    return SubmissionFull(
        submission_uuid=uuid.uuid4(),
        problem_id=1,
        user_uuid=uuid.uuid4(),
        language=Language.C,
        runtime_ms=5.21,
        mem_usage_mb=2.9,
        energy_usage_kwh=0.0,
        timestamp=timestamp,
        executed=True,
        successful=True,
        error_reason=None,
        error_msg=None,
        code="print(1)",
    )


@pytest.fixture(name="problem_list")
def problem_list_fixture() -> list[ProblemDetailsResponse]:
    return [
        ProblemDetailsResponse(
            problem_id=1,
            name="problem-name",
            language=Language.PYTHON,
            difficulty=Difficulty.EASY,
            tags=["tag122222"],
            short_description="descripton",
            long_description="long description",
            template_code="template code",
            wrapper=["a random wrapper"]
        )
    ]


@pytest.fixture(name="admin_authorization")
def admin_authorization_fixture():
    return data_to_jwt(
        JWTokenData(
            uuid=str(uuid.uuid4()), username="admin", permission_level=PermissionLevel.ADMIN
        ),
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM,
    )


@pytest.fixture(name="user_authorization")
def user_authorization_fixture():
    return data_to_jwt(
        JWTokenData(uuid=str(uuid.uuid4()), username="user", permission_level=PermissionLevel.USER),
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM,
    )


# Tests for actions module
def test_login_user_mocker(
    mocker: MockerFixture, session, user_login: LoginRequest, user_get: UserGet
):
    """Test that login_user retrieves the user and returns a TokenResponse."""
    mock_user_to_jwtokendata = mocker.patch("db.api.modules.actions.user_to_jwtokendata")
    mock_data_to_jwt = mocker.patch("db.api.modules.actions.data_to_jwt")
    mock_try_get_user_by_username = mocker.patch("db.engine.queries.try_get_user_by_username")

    mock_jwtokendata = JWTokenData(
        uuid=str(user_get.uuid), username="simon", permission_level=PermissionLevel.USER
    )

    mock_user_entry = UserEntry(
        uuid=user_get.uuid,
        username=user_get.username,
        email=user_get.email,
        permission_level=user_get.permission_level,
        hashed_password=hash_password(user_login.password),
    )

    mock_user_to_jwtokendata.return_value = mock_jwtokendata
    mock_try_get_user_by_username.return_value = mock_user_entry
    mock_data_to_jwt.return_value = "fake-jwt"

    result = actions.login_user(session, user_login)

    mock_try_get_user_by_username.assert_called_once_with(session, "simon")
    mock_user_to_jwtokendata.assert_called_once_with(user_get)
    mock_data_to_jwt.assert_called_once_with(
        mock_jwtokendata,
        settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        settings.JWT_ALGORITHM,
    )
    assert isinstance(result, TokenResponse)
    assert result.access_token == "fake-jwt"
    assert result.token_type == "bearer"


def test_lookup_user_result(mocker: MockerFixture, session, user_get):
    """Test that lookup_user retrieves the user by username and returns it."""
    mock_get_user = mocker.patch("db.api.modules.actions.ops.get_user_from_username")
    mock_get_user.return_value = user_get

    result = actions.lookup_user(session, "simon")

    mock_get_user.assert_called_once_with(session, "simon")
    assert result == user_get


# def test_get_leaderboard_result(mocker: MockerFixture, session, leaderboard_get):
#     """Test that get_leaderboard retrieves the leaderboard and returns it."""
#     mock_get_leaderboard = mocker.patch("db.api.modules.actions.ops.get_leaderboard")
#     mock_get_leaderboard.return_value = leaderboard_get

#     result = actions.get_leaderboard(session)

#     mock_get_leaderboard.assert_called_once_with(session)
#     assert result == leaderboard_get


def test_create_problem_mocker(
    mocker: MockerFixture, session, problem_request, admin_authorization
):
    """Test that create_problem actually calls ops.create_problem."""
    mock_create_problem = mocker.patch("db.api.modules.actions.ops.create_problem")
    # No return value needed for this test as it only asserts the call
    actions.create_problem(session, problem_request, admin_authorization)
    mock_create_problem.assert_called_once_with(session, problem_request)


def test_create_problem_result(
    login_session,
    problem_request,
    admin_authorization,
):
    """Test that create_problem returns a ProblemDetailsResponse with correct fiels."""
    result = actions.create_problem(login_session, problem_request, admin_authorization)
    assert isinstance(result, ProblemDetailsResponse)
    assert result.name == problem_request.name
    assert result.language == problem_request.language
    assert result.difficulty == problem_request.difficulty
    assert set(result.tags) == set(problem_request.tags)
    assert result.short_description == problem_request.short_description
    assert result.long_description == problem_request.long_description
    assert result.template_code == problem_request.template_code
    assert result.wrappers == problem_request.wrappers
    assert result.problem_id is not None


def test_create_submission_mocker(mocker: MockerFixture, session, submission_post):
    """Test that create_submission actually calls ops.create_submission."""
    mock_create_submission = mocker.patch("db.api.modules.actions.ops.create_submission")
    # No return value needed for this test as it only asserts the call
    actions.create_submission(session, submission_post)
    mock_create_submission.assert_called_once_with(session, submission_post)


def test_read_problems_result(mocker: MockerFixture, session, problem_list):
    """Test that read_problems returns a list of problems."""
    mock_read_problems = mocker.patch("db.api.modules.actions.ops.read_problems")
    mock_read_problems.return_value = problem_list

    result = actions.read_problems(session, offset=0, limit=10)

    mock_read_problems.assert_called_once_with(session, 0, 10)
    assert result == problem_list


def test_read_submissions_result(mocker: MockerFixture, session, mock_submission_get):
    """Test that read_submissions returns a list of submissions."""
    mock_get_submissions = mocker.patch("db.api.modules.actions.ops.get_submissions")
    mock_submissions_list = [mock_submission_get]
    mock_get_submissions.return_value = mock_submissions_list

    result = actions.read_submissions(session, offset=0, limit=10)

    mock_get_submissions.assert_called_once_with(session, 0, 10)
    assert result == mock_submissions_list


def test_get_problem_metadata_mocker(mocker: MockerFixture, session):
    """Test that get_problem_metadata calls ops.get_problem_metadata and returns correctly"""
    mock_summary = ProblemsListResponse(
        total=1,
        problems=[
            ProblemMetadata(
                problem_id=1,
                name="test",
                difficulty="easy",
                short_description="desc"
            )
        ]
    )

    mock_func = mocker.patch("db.api.modules.actions.ops.get_problem_metadata")
    mock_func.return_value = mock_summary

    result = actions.get_problem_metadata(session, offset=0, limit=10)

    mock_func.assert_called_once_with(session, 0, 10)
    assert result == mock_summary


def test_login_user_pass(
    login_session, user_1_register: RegisterRequest, user_1_login: LoginRequest
):
    """Test successful user login"""
    actions.register_user(login_session, user_1_register)
    actions.login_user(login_session, user_1_login)


def test_invalid_username_login_fail(login_session, user_1_login: LoginRequest):
    """Test username does not match constraints raises HTTPException with status 422"""
    with pytest.raises(HTTPException) as e:
        user_1_login.username = ""
        actions.login_user(login_session, user_1_login)

    assert e.value.status_code == 422
    assert e.value.detail == "PROB_USERNAME_CONSTRAINTS"


def test_incorrect_password_user_login_fail(
    login_session, user_1_register: RegisterRequest, user_1_login: LoginRequest
):
    """Test incorrect password raises HTTPException with status 401"""
    actions.register_user(login_session, user_1_register)
    actions.login_user(login_session, user_1_login)
    with pytest.raises(HTTPException) as e:
        user_1_login.password = "incorrect_password"
        actions.login_user(login_session, user_1_login)

    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"


def test_incorrect_username_user_login_fail(
    login_session, user_1_register: RegisterRequest, user_1_login: LoginRequest
):
    """Test incorrect username raises HTTPException with status 401"""
    actions.register_user(login_session, user_1_register)
    actions.login_user(login_session, user_1_login)
    with pytest.raises(HTTPException) as e:
        user_1_login.username = "IncorrectUsername"
        actions.login_user(login_session, user_1_login)

    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"


def test_user_login_result(
    login_session, user_1_register: RegisterRequest, user_1_login: LoginRequest
):
    """Test login user is correct user"""
    user_get_input = actions.register_user(login_session, user_1_register)
    user_get_output = actions.login_user(login_session, user_1_login)

    user_in = jwt_to_data(
        user_get_input.access_token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
    )
    user_out = jwt_to_data(
        user_get_output.access_token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
    )

    assert isinstance(user_in, JWTokenData)
    assert isinstance(user_out, JWTokenData)
    assert user_in == user_out


def test_get_leaderboard_success(
    mocker: MockerFixture,
    session,
    board_request,
    fake_leaderboard,
):
    """When ops returns a non-empty leaderboard and problem exists, return it unchanged."""
    mock_get_lb = mocker.patch(
        "db.api.modules.actions.ops.get_leaderboard",
        return_value=fake_leaderboard,
    )
    mocker.patch(
        "db.api.modules.actions.ops.try_get_problem",
        return_value=ProblemDetailsResponse(
            problem_id=1,
            name="demo",
            language="python",
            difficulty="easy",
            tags=[],
            short_description="",
            long_description="",
            template_code="",
            wrappers=[["", ""]],
        ),
    )

    result = actions.get_leaderboard(session, board_request)

    mock_get_lb.assert_called_once_with(session, board_request)
    assert result is fake_leaderboard


def test_get_leaderboard_no_problems_found(
    mocker: MockerFixture,
    session,
    board_request,
):
    """If ops.get_leaderboard returns None, or problem lookup fails, raise 400
    ERROR_NO_PROBLEMS_FOUND."""
    mocker.patch(
        "db.api.modules.actions.ops.get_leaderboard",
        return_value=None,
    )

    with pytest.raises(HTTPException) as exc:
        actions.get_leaderboard(session, board_request)

    assert exc.value.status_code == 400
    assert exc.value.detail == "ERROR_NO_PROBLEMS_FOUND"


def test_get_leaderboard_no_scores_found(
    mocker: MockerFixture,
    session,
    board_request,
    fake_leaderboard,
):
    """If ops returns empty .scores, raise 400 ERROR_NO_SCORES_FOUND."""
    empty_lb = LeaderboardResponse(
        problem_id=fake_leaderboard.problem_id,
        problem_name=fake_leaderboard.problem_name,
        problem_language=fake_leaderboard.problem_language,
        problem_difficulty=fake_leaderboard.problem_difficulty,
        scores=[],
    )
    mocker.patch(
        "db.api.modules.actions.ops.get_leaderboard",
        return_value=empty_lb,
    )
    mocker.patch(
        "db.api.modules.actions.ops.try_get_problem",
        return_value=ProblemDetailsResponse(
            problem_id=1,
            name="demo",
            language="python",
            difficulty="easy",
            tags=[],
            short_description="",
            long_description="",
            template_code="",
            wrapper=[["", ""]],
        ),
    )

    with pytest.raises(HTTPException) as exc:
        actions.get_leaderboard(session, board_request)

    assert exc.value.status_code == 400
    assert exc.value.detail == "ERROR_NO_SCORES_FOUND"
