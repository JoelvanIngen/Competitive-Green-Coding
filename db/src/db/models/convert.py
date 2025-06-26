from uuid import UUID

from common.languages import Language
from common.schemas import (
    AddProblemRequest,
    JWTokenData,
    ProblemDetailsResponse,
    ProblemMetadata,
    SubmissionCreate,
    SubmissionFull,
    SubmissionIdentifier,
    SubmissionMetadata,
    SubmissionResult,
    SubmissionRetrieveRequest,
    UserGet,
)
from common.typing import Difficulty
from db.models.db_schemas import ProblemEntry, SubmissionEntry, UserEntry


def db_user_to_user(db_user: UserEntry) -> UserGet:
    return UserGet(
        uuid=db_user.uuid,
        username=db_user.username,
        email=db_user.email,
        permission_level=db_user.permission_level,
        avatar_id=db_user.avatar_id,
        private=db_user.private,
    )


def submission_create_to_db_submission(submission: SubmissionCreate) -> SubmissionEntry:
    return SubmissionEntry(
        submission_uuid=submission.submission_uuid,
        problem_id=submission.problem_id,
        user_uuid=submission.user_uuid,
        language=submission.language,
        timestamp=submission.timestamp,
        executed=False,
        runtime_ms=0.00,
        mem_usage_mb=0.0,
        energy_usage_kwh=0.0,
        successful=False,
        error_reason=None,
        error_msg=None,
    )


def append_submission_results(submission: SubmissionEntry, result: SubmissionResult):
    """
    Takes a minimal entry that has been committed to the DB and fills in results.
    """

    submission.executed = True
    submission.runtime_ms = result.runtime_ms
    submission.mem_usage_mb = result.mem_usage_mb
    submission.energy_usage_kwh = result.energy_usage_kwh
    submission.successful = result.successful
    submission.error_reason = result.error_reason
    submission.error_msg = result.error_msg


def problem_post_to_db_problem(problem: AddProblemRequest) -> ProblemEntry:
    return ProblemEntry(
        name=problem.name,
        language=problem.language,
        difficulty=problem.difficulty,
        short_description=problem.short_description,
        long_description=problem.long_description,
    )


def db_submission_to_submission_create_response(
    submission: SubmissionEntry,
) -> SubmissionIdentifier:
    return SubmissionIdentifier(
        submission_uuid=submission.submission_uuid,
    )


def db_submission_to_submission_metadata(submission: SubmissionEntry) -> SubmissionMetadata:
    return SubmissionMetadata(
        submission_uuid=submission.submission_uuid,
        problem_id=submission.problem_id,
        user_uuid=submission.user_uuid,
        language=submission.language,
        runtime_ms=submission.runtime_ms,
        mem_usage_mb=submission.mem_usage_mb,
        energy_usage_kwh=submission.energy_usage_kwh,
        timestamp=submission.timestamp,
        executed=submission.executed,
        successful=submission.successful if submission.successful else False,  # Catch None
        error_reason=submission.error_reason,
    )


def db_submission_to_submission_full(submission: SubmissionEntry) -> SubmissionFull:
    return SubmissionFull(
        submission_uuid=submission.submission_uuid,
        problem_id=submission.problem_id,
        user_uuid=submission.user_uuid,
        language=submission.language,
        runtime_ms=submission.runtime_ms,
        mem_usage_mb=submission.mem_usage_mb,
        energy_usage_kwh=submission.energy_usage_kwh,
        timestamp=submission.timestamp,
        executed=submission.executed,
        successful=submission.successful if submission.successful else False,  # Catch None
        error_reason=submission.error_reason,
        error_msg=submission.error_msg,
        code="",  # Needs to be loaded from storage
    )


def db_problem_to_problem_get(db_problem: ProblemEntry) -> ProblemDetailsResponse:
    return ProblemDetailsResponse(
        problem_id=db_problem.problem_id,
        name=db_problem.name,
        language=db_problem.language,
        difficulty=db_problem.difficulty,
        tags=[problem_tag_entry.tag for problem_tag_entry in db_problem.tags],
        short_description=db_problem.short_description,
        long_description=db_problem.long_description,
        template_code="",  # Needs to be loaded from storage
        wrappers=[["", ""]],  # Needs to be loaded from storage
    )


def user_to_jwtokendata(user: UserGet):
    return JWTokenData(
        uuid=str(user.uuid),
        username=user.username,
        permission_level=user.permission_level,
        avatar_id=user.avatar_id,
    )


def db_problem_to_metadata(problem: ProblemEntry) -> ProblemMetadata:
    # This function converts a ProblemEntry to a ProblemMetadata.
    return ProblemMetadata(
        problem_id=problem.problem_id,
        name=problem.name,
        difficulty=Difficulty(problem.difficulty),
        short_description=problem.short_description,
    )


def create_submission_retrieve_request(
    problem_id: int, user_uuid: UUID, language: Language
) -> SubmissionRetrieveRequest:
    """Creates SubmissionRetrieveRequest which can be used to retrieve the submission.

    Args:
        problem_id (int): id of the problem
        user_uuid (UUID): uuid of the user
        language (Language): language of the problem

    Returns:
        SubmissionRetrieveRequest: request schema to retrieve submission with
    """

    return SubmissionRetrieveRequest(problem_id=problem_id, user_uuid=user_uuid, language=language)
