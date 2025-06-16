import os

from common.languages import Language
from common.typing import SubmissionType
from db import settings


def framework_path(language: Language):
    return os.path.join(
        settings.DB_HANDLER_STORAGE_PATH,
        settings.FRAMEWORK_DIR_DIR,
        language.name,
    )


def _submission_path(problem_id: str, user_uuid: str):
    return os.path.join(
        settings.DB_HANDLER_STORAGE_PATH,
        settings.CODE_SUBMISSION_DIR,
        problem_id,
        user_uuid,
    )


def wrapper_path(language: Language):
    return os.path.join(
        settings.DB_HANDLER_STORAGE_PATH,
        settings.WRAPPER_DIR,
        language.name,
    )


def submission_code_path(submission: SubmissionType):
    return _submission_path(submission.problem_id, submission.user_uuid)
