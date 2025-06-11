import os
import shutil
import tarfile
import tempfile

import httpx
from loguru import logger

from execution_engine.config import settings
from execution_engine.docker.languages import language_info
from execution_engine.docker.runconfig import RunConfig
from execution_engine.typing import LanguageLiteral


def _unpack_tarball(path: str) -> None:
    with tarfile.open(path) as tar:
        tar.extractall()


def _copy_framework(tmpdir: str, language: LanguageLiteral):
    """
    Copies existing framework to environment
    TODO: Can raise exceptions, catch those
    """
    path = os.path.join("/frameworks", language_info[language].name)
    for file_name in os.listdir(path):
        src_item_path = os.path.join(path, file_name)
        dst_item_path = os.path.join(tmpdir, file_name)
        if not os.path.isfile(src_item_path):
            continue

        shutil.copy2(src_item_path, dst_item_path)


async def _request_and_copy_wrapper(tmpdir: str, language: LanguageLiteral):
    """
    Copies existing wrapper to environment, downloading files from DB handler
    """
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream(
                "GET",
                f"{settings.DB_HANDLER_URL}/api/wrapper/{language_info[language].name}",
            ) as response:
                response.raise_for_status()
                filename = f"{tmpdir}/wrapper.tar.gz"
                with open(tmpdir, "wb") as f:
                    f.write(response.content)

        except httpx.RequestError as e:
            logger.error(f"Network error during tarball download: {e}")
            raise e
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during tarball download: {e}")
            raise e

    try:
        _unpack_tarball(filename)
    finally:
        os.remove(filename)


def _store_submission(tmpdir: str, language: LanguageLiteral, code: str):
    """
    Stores the received submission in the environment
    """
    extension = language_info[language].file_extension
    filename = f"submission.{extension}"
    with open(os.path.join(tmpdir, filename), "w") as f:
        f.write(code)


def _create_tmp_dir() -> str:
    return tempfile.mkdtemp(
        dir="/container_files", prefix=settings.EXECUTION_ENVIRONMENT_TMP_DIR_PREFIX
    )


async def setup_env(config: RunConfig, code):
    """
    Sets up the environment and stores temp dir in the config
    """
    tmp_dir = _create_tmp_dir()
    _copy_framework(tmp_dir, config.origin_request.language)
    await _request_and_copy_wrapper(tmp_dir, config.origin_request.language)
    _store_submission(tmp_dir, config.origin_request.language, code)
    config.tmp_dir = tmp_dir
