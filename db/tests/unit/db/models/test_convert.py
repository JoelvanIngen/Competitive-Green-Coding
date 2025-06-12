import pytest
from pydantic import ValidationError
from db.models.convert import (
    db_user_to_user,
    submission_post_to_db_submission,
    db_submission_to_submission_get,
    db_problem_to_problem_get,
    SubmissionPost,
)


def test_db_user_to_user(user_entry_fixture, user_get_fixture):
    assert db_user_to_user(user_entry_fixture) == user_get_fixture


def test_submission_post_to_db_submission(submission_post_fixture, submission_entry_fixture):
    assert submission_post_to_db_submission(submission_post_fixture) == submission_entry_fixture


def test_db_submission_to_submission_get(db_submission_for_get_fixture, submission_get_fixture):
    assert db_submission_to_submission_get(db_submission_for_get_fixture) == submission_get_fixture


def test_db_problem_to_problem_get(problem_entry_fixture, problem_get_fixture):
    assert db_problem_to_problem_get(problem_entry_fixture) == problem_get_fixture


def test_submission_symmetry(submission_entry_fixture):
    get_obj = db_submission_to_submission_get(submission_entry_fixture)
    roundtrip_entry = submission_post_to_db_submission(get_obj)

    assert roundtrip_entry.problem_id == submission_entry_fixture.problem_id
    assert roundtrip_entry.uuid == submission_entry_fixture.uuid
    assert roundtrip_entry.runtime_ms == submission_entry_fixture.runtime_ms
    assert roundtrip_entry.timestamp == submission_entry_fixture.timestamp
    assert roundtrip_entry.successful == submission_entry_fixture.successful


def test_submission_post_missing_runtime(submission_post_missing_runtime_fixture):
    # TODO: what error do we want to raise here?
    with pytest.raises(ValidationError):
        SubmissionPost(**submission_post_missing_runtime_fixture)
