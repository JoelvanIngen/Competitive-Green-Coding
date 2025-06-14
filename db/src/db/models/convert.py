from common.schemas import (
    JWTokenData,
    ProblemGet,
    ProblemPost,
    SubmissionGet,
    SubmissionPost,
    UserGet, SubmissionCreate, SubmissionResult, SubmissionMetadataGet, SubmissionFullGet,
)
from db.models.calculate_score import get_score
from db.models.db_schemas import ProblemEntry, SubmissionEntry, UserEntry


def db_user_to_user(db_user: UserEntry) -> UserGet:
    return UserGet(
        uuid=db_user.uuid,
        username=db_user.username,
        email=db_user.email,
        permission_level=db_user.permission_level,
    )


def submission_create_to_db_submission(submission: SubmissionCreate) -> SubmissionEntry:
    return SubmissionEntry(
        submission_uuid=submission.submission_uuid,
        problem_id=submission.problem_id,
        user_uuid=submission.user_uuid,
        language=submission.language,
        timestamp=submission.timestamp,
        executed=False,
        runtime_ms=0,
        mem_usage_mb=0.,
        success=False,
        error_reason=None,
        error_msg=None,
    )


def append_submission_results(submission: SubmissionEntry, result: SubmissionResult) -> SubmissionEntry:
    """
    Takes a minimal entry that has been committed to the DB and fills in results.
    Returns a new object.
    """

    return SubmissionEntry(
        submission_uuid=submission.submission_uuid,
        problem_id=submission.problem_id,
        user_uuid=submission.user_uuid,
        language=submission.language,
        timestamp=submission.timestamp,
        executed=True,
        runtime_ms=result.runtime_ms,
        mem_usage_mb=result.mem_usage_mb,
        success=result.success,
        error_reason=result.error_reason,
        error_msg=result.error_msg,
    )


# def submission_post_to_db_submission(submission: SubmissionPost) -> SubmissionEntry:
#     ### NOTE TO REVIEWER: CAN WE SAFELY REMOVE THIS FUNCTION?
#     return SubmissionEntry(
#         problem_id=submission.problem_id,
#         uuid=submission.uuid,
#         runtime_ms=submission.runtime_ms,
#         timestamp=submission.timestamp,
#         successful=submission.successful,
#         score=get_score(submission.runtime_ms),
#     )


def problem_post_to_db_problem(problem: ProblemPost) -> ProblemEntry:
    return ProblemEntry(
        name=problem.name,
        language=problem.language,
        difficulty=problem.difficulty,
        short_description=problem.short_description,
        long_description=problem.long_description,
        template_code=problem.template_code,
    )


def db_submission_to_submission_metadata(submission: SubmissionEntry) -> SubmissionMetadataGet:
    return SubmissionMetadataGet(
        submission_uuid=submission.submission_uuid,
        problem_id=submission.problem_id,
        user_uuid=submission.user_uuid,
        language=submission.language,
        runtime_ms=submission.runtime_ms,
        mem_usage_mb=submission.mem_usage_mb,
        timestamp=submission.timestamp,
        success=submission.success,
        error_reason=submission.error_reason,
    )


def db_submission_to_submission_full(submission: SubmissionEntry) -> SubmissionFullGet:
    return SubmissionFullGet(
        submission_uuid=submission.submission_uuid,
        problem_id=submission.problem_id,
        user_uuid=submission.user_uuid,
        language=submission.language,
        runtime_ms=submission.runtime_ms,
        mem_usage_mb=submission.mem_usage_mb,
        timestamp=submission.timestamp,
        executed=submission.success,
        success=submission.success,
        error_reason=submission.error_reason,
        error_msg=submission.error_msg,
        code="",  # Needs to be loaded from storage
    )


def db_problem_to_problem_get(db_problem: ProblemEntry) -> ProblemGet:
    return ProblemGet(
        problem_id=db_problem.problem_id,
        name=db_problem.name,
        language=db_problem.language,
        difficulty=db_problem.difficulty,
        tags=[problem_tag_entry.tag for problem_tag_entry in db_problem.tags],
        short_description=db_problem.short_description,
        long_description=db_problem.long_description,
        template_code=db_problem.template_code,
    )


def user_to_jwtokendata(user: UserGet):
    return JWTokenData(
        uuid=str(user.uuid), username=user.username, permission_level=user.permission_level
    )
