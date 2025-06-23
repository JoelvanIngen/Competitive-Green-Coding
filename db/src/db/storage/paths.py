import os

from common.languages import Language
from common.schemas import SubmissionCreate, SubmissionMetadata
from db import settings


def framework_path(language: Language):
    return os.path.join(
        settings.DB_HANDLER_STORAGE_PATH,
        settings.FRAMEWORK_DIR,
        language.name,
    )


def _submission_path(problem_id: str, user_uuid: str):
    return os.path.join(
        settings.DB_HANDLER_STORAGE_PATH,
        settings.CODE_SUBMISSION_DIR,
        problem_id,
        user_uuid,
    )


def template_path(problem_id: str, language_name: str):
    return os.path.join(
        settings.DB_HANDLER_STORAGE_PATH,
        settings.TEMPLATE_DIR,
        problem_id,
        language_name,
    )


def wrapper_path(problem_id: str, language_name: str):
    return os.path.join(
        settings.DB_HANDLER_STORAGE_PATH,
        settings.WRAPPER_DIR,
        problem_id,
        language_name,
    )


def submission_code_path(submission: SubmissionCreate | SubmissionMetadata):
    return _submission_path(str(submission.problem_id), str(submission.user_uuid))
