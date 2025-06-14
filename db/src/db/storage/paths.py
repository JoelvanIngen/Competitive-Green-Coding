import os

from common.schemas import SubmissionPost


def submission_post_to_dir(s: SubmissionPost):
    return os.path.join(
        str(s.problem_id),
        str(s.uuid),
    )
