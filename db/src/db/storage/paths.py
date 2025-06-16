import os

from common.schemas import SubmissionCreate, SubmissionMetadata


def _submission_path(problem_id: str, user_uuid: str) -> str:
    return os.path.join(
        "storage",
        problem_id,
        user_uuid,
    )


def submission_create_to_dir(s: SubmissionCreate):
    return _submission_path(str(s.problem_id), str(s.user_uuid))


def submission_metadata_to_dir(s: SubmissionMetadata):
    return _submission_path(str(s.problem_id), str(s.user_uuid))
