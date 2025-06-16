import io

from common.languages import Language
from common.schemas import SubmissionCreate, SubmissionFull, SubmissionMetadata
from db.storage.io import write_file, read_file, read_folder_to_tar
from db.storage.paths import submission_code_path, wrapper_path, framework_path


def load_framework_tar(language: Language) -> io.BytesIO:
    path = framework_path(language)

    return read_folder_to_tar(path)


def load_last_submission_code(submission: SubmissionMetadata) -> str:
    path = submission_code_path(submission)

    language: Language = submission.language
    return read_file(path, f"latest.{language.info.file_extension}")


def load_wrapper_tar(language: Language) -> io.BytesIO:
    path = wrapper_path(language)

    return read_folder_to_tar(path)


def store_code(submission: SubmissionCreate) -> None:
    path = submission_code_path(submission)

    language: Language = submission.language
    write_file(submission.code, path, f"latest.{language.info.file_extension}")
