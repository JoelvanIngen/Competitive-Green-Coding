import os
import re
import stat
import tarfile
import tempfile

import httpx
from loguru import logger

from common.languages import Language, language_info
from common.schemas import SubmissionCreate
from execution_engine.config import settings
from execution_engine.docker_handler.runconfig import RunConfig
from execution_engine.docker_handler.state import client


def _ensure_image_pulled(config: RunConfig):
    client.images.pull(config.language.image)


def _unpack_tarball(path: str) -> None:
    dir_path = os.path.dirname(path)
    with tarfile.open(path) as tar:
        tar.extractall(dir_path)


async def _request_framework_files(tmp_dir: str, submission: SubmissionCreate):
    filename = os.path.join(tmp_dir, "framework.tar.gz")

    async with httpx.AsyncClient() as http_client:
        try:
            async with http_client.stream(
                "POST",
                f"{settings.DB_HANDLER_URL}/api/framework",
                content=submission.model_dump_json(),
                headers={"Content-Type": "application/json"},
            ) as response:
                response.raise_for_status()

                content_disposition = response.headers.get("Content-Disposition")
                if content_disposition:
                    # Find filename in header
                    match = re.search(r'filename="([^"]+)"', content_disposition)
                    if match:
                        filename = os.path.join(tmp_dir, match.group(1))

                with open(filename, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)

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


def _store_submission(tmpdir: str, language: Language, code: str):
    """
    Stores the received submission in the environment
    """
    extension = language_info[language].file_extension
    filename = f"submission.{extension}"
    with open(os.path.join(tmpdir, filename), "w") as f:
        f.write(code)


def _create_tmp_dir() -> str:
    if not os.path.exists(settings.TMP_DIR_PATH_BASE):
        os.makedirs(settings.TMP_DIR_PATH_BASE)

    return os.path.abspath(
        tempfile.mkdtemp(
            dir=settings.TMP_DIR_PATH_BASE, prefix=settings.EXECUTION_ENVIRONMENT_TMP_DIR_PREFIX
        )
    )


def _chmod_run_script(tmp_dir: str):
    run_sh_path = os.path.join(tmp_dir, "run.sh")
    current_permissions = os.stat(run_sh_path).st_mode
    os.chmod(run_sh_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


async def setup_env(config: RunConfig, code):
    """
    Sets up the environment and stores temp dir in the config
    """
    _ensure_image_pulled(config)
    tmp_dir = _create_tmp_dir()
    await _request_framework_files(tmp_dir, config.origin_request)
    _store_submission(tmp_dir, config.origin_request.language, code)
    config.tmp_dir = tmp_dir
    _chmod_run_script(tmp_dir)
