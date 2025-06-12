import pytest
from pydantic import ValidationError
from db.models.convert import (
    db_user_to_user,
    submission_post_to_db_submission,
    db_submission_to_submission_get,
    db_problem_to_problem_get,
)


def test_db_user_to_user(user_entry_fixture, user_get_fixture):
    assert db_user_to_user(user_entry_fixture) == user_get_fixture


def test_submission_post_to_db_submission(submission_post_fixture, submission_entry_fixture):
    assert submission_post_to_db_submission(submission_post_fixture) == submission_entry_fixture


def test_db_submission_to_submission_get(db_submission_for_get_fixture, submission_get_fixture):
    assert db_submission_to_submission_get(db_submission_for_get_fixture) == submission_get_fixture


def test_db_problem_to_problem_get(problem_entry_fixture, problem_get_fixture):
    assert db_problem_to_problem_get(problem_entry_fixture) == problem_get_fixture

def test_submission_post_missing_runtime(submission_post_missing_runtime_fixture):
    # TODO: what error do we want to raise here?
    with pytest.raises(ValidationError):
        SubmissionPost(**submission_post_missing_runtime_fixture)
