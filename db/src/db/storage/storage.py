import io
import os
import tarfile
from tarfile import TarFile

from common.languages import Language
from common.schemas import (
    ProblemDetailsResponse,
    SubmissionCreate,
    SubmissionMetadata,
    SubmissionRetrieveRequest,
)
from db.storage.io import read_file, read_file_to_tar, read_folder_to_tar, write_file
from db.storage.paths import framework_path, submission_code_path, template_path, wrapper_path


def _add_framework_to_tar(tar: TarFile, language: Language) -> None:
    read_folder_to_tar(tar, framework_path(language))


def _add_submission_to_tar(tar: TarFile, sub: SubmissionCreate | SubmissionMetadata) -> None:
    read_file_to_tar(tar, submission_code_path(sub))


def _add_wrapper_to_tar(tar: TarFile, sub: SubmissionCreate | SubmissionMetadata) -> None:
    read_folder_to_tar(tar, wrapper_path(str(sub.problem_id), sub.language.info.name))


def load_last_submission_code(submission: SubmissionMetadata | SubmissionRetrieveRequest) -> str:
    path = submission_code_path(submission)

    language: Language = submission.language
    return read_file(path, f"latest.{language.info.file_extension}")


def load_template_code(problem: ProblemDetailsResponse) -> str:
    path = template_path(str(problem.problem_id), problem.language)

    return read_file(path, f"template.{problem.language.info.file_extension}")


def load_wrapper_code(problem: ProblemDetailsResponse) -> list[list[str]]:
    path = wrapper_path(str(problem.problem_id), problem.language)
    wrappers: list[list[str]] = []

    if not os.path.exists(path):
        return wrappers

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                wrappers.append([filename, content])

    return wrappers


def tar_full_framework(submission: SubmissionCreate) -> io.BytesIO:
    """
    Creates a gzipped tar archive in an in-memory buffer.
    This function is SYNCHRONOUS and should be run in a thread pool.
    """
    buff = io.BytesIO()
    with tarfile.open(fileobj=buff, mode="w:gz") as tar:
        _add_framework_to_tar(tar, submission.language)
        _add_wrapper_to_tar(tar, submission)

    buff.seek(0)
    return buff


def store_code(submission: SubmissionCreate) -> None:
    path = submission_code_path(submission)

    language: Language = submission.language
    write_file(submission.code, path, f"latest.{language.info.file_extension}")


def store_template_code(problem: ProblemDetailsResponse):
    path = template_path(str(problem.problem_id), problem.language)
    write_file(problem.template_code, path, f"template.{problem.language.info.file_extension}")


def store_wrapper_code(problem: ProblemDetailsResponse):
    path = wrapper_path(str(problem.problem_id), problem.language)

    for wrapper in problem.wrappers:
        filename = wrapper[0]
        content = wrapper[1]
        write_file(content, path, filename)
