import io
import tarfile
from tarfile import TarFile

from common.languages import Language
from common.schemas import SubmissionCreate, SubmissionMetadata
from db.storage.io import read_file, read_file_to_tar, read_folder_to_tar, write_file
from db.storage.paths import framework_path, submission_code_path, wrapper_path


def _add_framework_to_tar(tar: TarFile, language: Language) -> None:
    read_folder_to_tar(tar, framework_path(language))


def _add_submission_to_tar(tar: TarFile, sub: SubmissionCreate | SubmissionMetadata) -> None:
    read_file_to_tar(tar, submission_code_path(sub))


def _add_wrapper_to_tar(tar: TarFile, sub: SubmissionCreate | SubmissionMetadata) -> None:
    read_folder_to_tar(tar, wrapper_path(str(sub.problem_id), sub.language.name))


def load_last_submission_code(submission: SubmissionMetadata) -> str:
    path = submission_code_path(submission)

    language: Language = submission.language
    return read_file(path, f"latest.{language.info.file_extension}")


def tar_full_framework(submission: SubmissionCreate) -> io.BytesIO:
    buff = io.BytesIO()
    with tarfile.open(fileobj=buff, mode="w:gz") as tar:
        _add_framework_to_tar(tar, submission.language)
        _add_wrapper_to_tar(tar, submission)

    return buff


def store_code(submission: SubmissionCreate) -> None:
    path = submission_code_path(submission)

    language: Language = submission.language
    write_file(submission.code, path, f"latest.{language.info.file_extension}")
