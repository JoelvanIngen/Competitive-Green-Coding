from db.models.db_schemas import ProblemEntry, SubmissionEntry, UserEntry
from db.models.schemas import ProblemGet, SubmissionPost, UserGet


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
        code=submission.code,
    )


def db_problem_to_problem_get(db_problem: ProblemEntry) -> ProblemGet:
    return ProblemGet(
        problem_id=db_problem.problem_id,
        name=db_problem.name,
        description=db_problem.description,
        tags=[],
    )
