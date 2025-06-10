import os
from typing import TextIO, cast, get_args

from loguru import logger

from execution_engine.config import settings
from execution_engine.models.schemas import ExecuteRequest, ExecuteResult, StatusType

from . import async_file_ops
from .docker_manager import DockerManager, DockerStatus


class _ExecutionData:
    def __init__(self, tmp_dir: str) -> None:
        self.tmp_dir: str

        self.compile_stdout_file = os.path.join(tmp_dir, settings.COMPILE_STDOUT_FILE_NAME)
        self.compile_stderr_file = os.path.join(tmp_dir, settings.COMPILE_STDERR_FILE_NAME)
        self.run_stdout_file = os.path.join(tmp_dir, settings.RUN_STDOUT_FILE_NAME)
        self.run_stderr_file = os.path.join(tmp_dir, settings.RUN_STDERR_FILE_NAME)
        self.fail_file = os.path.join(tmp_dir, settings.FAILED_FILE_NAME)


class Executor:
    def __init__(self) -> None:
        self._docker_manager = DockerManager()

    async def _setup_environment(self, tmp_dir: str, code: str):
        raise NotImplementedError()

    async def execute_code(self, request: ExecuteRequest) -> ExecuteResult:
        code = await _request_code(request)

        tmp_dir = None

        try:
            tmp_dir = await async_file_ops.create_tmp_dir()

            await self._setup_environment(tmp_dir, code)

            volumes = {tmp_dir: {"bind": "/app", "mode": "rw"}}

            docker_status = await self._docker_manager.run_container(
                image=settings.EXECUTION_ENVIRONMENT_IMAGE_NAME,
                command=["/bin/bash", settings.CONTAINER_SCRIPT],
                volumes=volumes,
                working_dir=settings.EXECUTION_ENVIRONMENT_APP_DIR,
            )

            # Early return if Docker failed or OOM/timeout occurred
            if docker_status != DockerStatus.SUCCESS:
                return ExecuteResult(
                    status=docker_status.to_status_t(),
                    runtime_ms=0,
                    mem_usage_mb=0,
                    error_msg="",
                )

            data = _ExecutionData(tmp_dir)
            return await _parse_output_files(data)

        except Exception as e:
            logger.error(e)
            raise e

        finally:
            if tmp_dir:
                await async_file_ops.delete_tmp_dir(tmp_dir)


async def _parse_output_files(data: _ExecutionData) -> ExecuteResult:
    # Check for reported errors
    if os.path.exists(data.fail_file):
        # Some reported error occurred
        with open(data.fail_file, "r") as f:
            return await _parse_error_file(data, f)

    # TODO: Check if submission output is correct

    # Dummy result to make type checker happy for now
    return ExecuteResult(status="success", runtime_ms=0, mem_usage_mb=0, error_msg="")


async def _parse_error_file(data: _ExecutionData, f: TextIO) -> ExecuteResult:
    """
    Reads the created error file and fills the result based on the reported
    error
    """
    error = f.readline().strip()

    # Ensure error type is one of the allowed types
    if error not in get_args(StatusType):
        raise NotImplementedError(f"Received non-existent error {error} in failed.txt")
    error = cast(StatusType, error)

    result = ExecuteResult(
        runtime_ms=0,
        mem_usage_mb=0,
        status=error,
        error_msg="",
    )

    match error:
        case "timeout":
            # Don't delete this, it's here so it doesn't get reported as
            # unexpected error
            pass
        case "compile_error":
            with open(data.compile_stderr_file, "r") as f:
                result.error_msg = f.read()
        case "runtime_error":
            with open(data.run_stderr_file, "r") as f:
                result.error_msg = f.read()
        case _:
            # I don't expect any other errors from the fail file
            raise NotImplementedError(
                f"Received unexpected error {error} in {settings.FAILED_FILE_NAME}"
            )

    return result


async def _request_code(request: ExecuteRequest) -> str:
    raise NotImplementedError(request)
