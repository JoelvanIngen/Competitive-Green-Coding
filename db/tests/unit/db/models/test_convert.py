"""
Test verifies whether all schema fields are copied correctly, additionally
whether:
*   A PermissionLevel enum is passed through,
*   Code field in submissions is set to "",
*   Tags array in problem is initialized empty,
"""

import pytest
from db.models.convert import (
    db_user_to_user,
    submission_post_to_db_submission,
    db_submission_to_submission_get,
    db_problem_to_problem_get,
)


def test_db_user_to_user(sample_user_entry, expected_user_get):
    assert db_user_to_user(sample_user_entry) == expected_user_get


def test_submission_post_to_db_submission(sample_submission_post, sample_submission_entry):
    assert submission_post_to_db_submission(sample_submission_post) == sample_submission_entry


def test_db_submission_to_submission_get(sample_db_submission_for_get, expected_submission_get):
    assert db_submission_to_submission_get(sample_db_submission_for_get) == expected_submission_get


def test_db_problem_to_problem_get(sample_problem_entry, expected_problem_get):
    assert db_problem_to_problem_get(sample_problem_entry) == expected_problem_get
