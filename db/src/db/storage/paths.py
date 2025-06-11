import os

from db.models.schemas import SubmissionPost


def submission_post_to_dir(s: SubmissionPost):
    return os.path.join(
        str(s.problem_id),
        str(s.uuid),
        'submission.c',  # Hardcode C for now
    )
