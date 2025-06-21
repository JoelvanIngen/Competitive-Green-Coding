import pytest
from uuid import UUID

from db.models.convert import (
    db_user_to_user,
    submission_create_to_db_submission,
    append_submission_results,
    problem_post_to_db_problem,
    db_submission_to_submission_metadata,
    db_submission_to_submission_full,
    db_problem_to_problem_get,
    user_to_jwtokendata,
    db_problem_to_metadata
)


def test_db_user_to_user(user_entry_fixture, user_get_fixture):
    """Test conversion of UserEntry to UserGet schema"""
    result = db_user_to_user(user_entry_fixture)

    assert result.uuid == user_get_fixture.uuid
    assert result.username == user_get_fixture.username
    assert result.email == user_get_fixture.email
    assert result.permission_level == user_get_fixture.permission_level

    assert not hasattr(result, "hashed_password")


def test_submission_create_to_db_submission(submission_create_fixture):
    """Test conversion of SubmissionCreate to SubmissionEntry"""
    result = submission_create_to_db_submission(submission_create_fixture)

    assert result.submission_uuid == submission_create_fixture.submission_uuid
    assert result.problem_id == submission_create_fixture.problem_id
    assert result.user_uuid == submission_create_fixture.user_uuid
    assert result.language == submission_create_fixture.language
    assert result.timestamp == submission_create_fixture.timestamp

    assert result.executed is False
    assert result.runtime_ms == 0.00
    assert result.mem_usage_mb == 0.0
    assert result.energy_usage_kwh == 0.0
    assert result.successful is False
    assert result.error_reason is None
    assert result.error_msg is None

    assert not hasattr(result, "code")


def test_append_submission_results(submission_entry_fixture, submission_result_fixture):
    """Test updating SubmissionEntry with SubmissionResult"""
    submission = type(submission_entry_fixture)(**submission_entry_fixture.__dict__)
    append_submission_results(submission, submission_result_fixture)

    assert submission.runtime_ms == submission_result_fixture.runtime_ms
    assert submission.mem_usage_mb == submission_result_fixture.mem_usage_mb
    assert submission.energy_usage_kwh == submission_result_fixture.energy_usage_kwh
    assert submission.successful == submission_result_fixture.successful
    assert submission.error_reason == submission_result_fixture.error_reason
    assert submission.error_msg == submission_result_fixture.error_msg

    assert submission.executed is True

    assert submission.submission_uuid == submission_entry_fixture.submission_uuid
    assert submission.problem_id == submission_entry_fixture.problem_id
    assert submission.user_uuid == submission_entry_fixture.user_uuid
    assert submission.language == submission_entry_fixture.language
    assert submission.timestamp == submission_entry_fixture.timestamp


def test_problem_post_to_db_problem(problem_post_fixture):
    """Test conversion of AddProblemRequest to ProblemEntry"""
    result = problem_post_to_db_problem(problem_post_fixture)

    assert result.name == problem_post_fixture.name
    assert result.language == problem_post_fixture.language
    assert result.difficulty == problem_post_fixture.difficulty
    assert result.short_description == problem_post_fixture.short_description
    assert result.long_description == problem_post_fixture.long_description
    assert result.template_code == problem_post_fixture.template_code

    assert not hasattr(result, "problem_id") or result.problem_id is None



def test_db_submission_to_submission_metadata(
    submission_entry_fixture, submission_metadata_fixture
):
    """Test conversion to SubmissionMetadata schema"""
    result = db_submission_to_submission_metadata(submission_entry_fixture)

    assert result.submission_uuid == submission_metadata_fixture.submission_uuid
    assert result.problem_id == submission_metadata_fixture.problem_id
    assert result.user_uuid == submission_metadata_fixture.user_uuid
    assert result.language == submission_metadata_fixture.language
    assert result.runtime_ms == submission_metadata_fixture.runtime_ms
    assert result.mem_usage_mb == submission_metadata_fixture.mem_usage_mb
    assert result.timestamp == submission_metadata_fixture.timestamp
    assert result.executed == submission_metadata_fixture.executed
    assert result.successful == submission_metadata_fixture.successful
    assert result.error_reason == submission_metadata_fixture.error_reason

    assert not hasattr(result, "error_msg")

    assert not hasattr(result, "code")


def test_db_submission_to_submission_full(submission_entry_fixture, submission_full_fixture):
    """Test conversion to SubmissionFull schema"""
    result = db_submission_to_submission_full(submission_entry_fixture)

    assert result.submission_uuid == submission_full_fixture.submission_uuid
    assert result.problem_id == submission_full_fixture.problem_id
    assert result.user_uuid == submission_full_fixture.user_uuid
    assert result.language == submission_full_fixture.language
    assert result.runtime_ms == submission_full_fixture.runtime_ms
    assert result.mem_usage_mb == submission_full_fixture.mem_usage_mb
    assert result.timestamp == submission_full_fixture.timestamp
    assert result.executed == submission_full_fixture.executed
    assert result.successful == submission_full_fixture.successful
    assert result.error_reason == submission_full_fixture.error_reason
    assert result.error_msg == submission_full_fixture.error_msg

    assert result.code == ""

    assert set(result.model_dump().keys()) == set(submission_full_fixture.model_dump().keys())


def test_db_problem_to_problem_get(problem_entry_fixture, problem_get_fixture):
    """Test conversion of ProblemEntry to ProblemDetailsResponse schema"""
    result = db_problem_to_problem_get(problem_entry_fixture)

    assert result.problem_id == problem_get_fixture.problem_id
    assert result.name == problem_get_fixture.name
    assert result.language == problem_get_fixture.language
    assert result.difficulty == problem_get_fixture.difficulty
    assert result.short_description == problem_get_fixture.short_description
    assert result.long_description == problem_get_fixture.long_description
    assert result.template_code == problem_get_fixture.template_code

    assert set(result.tags) == {"test", "python"}
    assert len(result.tags) == 2

    assert not hasattr(result, "problem_tag_entries")


def test_user_to_jwtokendata(user_get_fixture, jwt_token_data_fixture):
    """Test conversion of UserGet to JWTokenData"""
    result = user_to_jwtokendata(user_get_fixture)

    assert result.uuid == str(user_get_fixture.uuid)
    assert result.username == user_get_fixture.username
    assert result.permission_level == user_get_fixture.permission_level

    assert not hasattr(result, "email")

    assert set(result.model_dump().keys()) == {"uuid", "username", "permission_level"}

def test_db_problem_to_metadata(problem_entry_fixture):
    """Test conversion of ProblemEntry to ProblemMetadata"""
    summary = db_problem_to_metadata(problem_entry_fixture)

    assert summary.problem_id == problem_entry_fixture.problem_id
    assert summary.name == problem_entry_fixture.name
    assert summary.difficulty == problem_entry_fixture.difficulty
    assert summary.short_description == problem_entry_fixture.short_description
