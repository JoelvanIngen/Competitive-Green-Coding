from db.models.db_schemas import UserEntry, SubmissionEntry
from db.models.schemas import UserGet, SubmissionPost


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
