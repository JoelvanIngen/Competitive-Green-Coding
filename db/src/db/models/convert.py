from db.models.calculate_score import get_score
from db.models.db_schemas import ProblemEntry, SubmissionEntry, UserEntry
from db.models.schemas import (
    JWTokenData,
    ProblemGet,
    ProblemPost,
    SubmissionGet,
    SubmissionPost,
    UserGet,
)


def db_user_to_user(db_user: UserEntry) -> UserGet:
    return UserGet(
        uuid=db_user.uuid,
        username=db_user.username,
        email=db_user.email,
        permission_level=db_user.permission_level,
    )


def submission_post_to_db_submission(submission: SubmissionPost) -> SubmissionEntry:
    return SubmissionEntry(
        problem_id=submission.problem_id,
        uuid=submission.uuid,
        runtime_ms=submission.runtime_ms,
        timestamp=submission.timestamp,
        successful=submission.successful,
        score=get_score(submission.runtime_ms),
    )


def problem_post_to_db_problem(problem: ProblemPost) -> ProblemEntry:
    return ProblemEntry(
        name=problem.name,
        language=problem.language,
        difficulty=problem.difficulty,
        short_description=problem.short_description,
        long_description=problem.long_description,
        template_code=problem.template_code,
    )


def db_submission_to_submission_get(submission: SubmissionEntry) -> SubmissionGet:
    # TODO: Load code from disk when necessary
    #       OR: Split in two;
    #           - SubmissionMetadata (doesn't contain code)
    #           - Submission (does contain code)
    #       We don't want to send all code for for example a leaderboard
    return SubmissionGet(
        sid=submission.sid,
        problem_id=submission.problem_id,
        uuid=submission.uuid,
        score=submission.runtime_ms,
        timestamp=submission.timestamp,
        successful=submission.successful,
        code="",
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
