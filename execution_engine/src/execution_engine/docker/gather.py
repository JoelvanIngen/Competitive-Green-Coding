import os

from execution_engine.config import settings
from execution_engine.docker.runconfig import RunConfig
from execution_engine.errors.errors import (
    CompileFailedError,
    RuntimeFailError,
    TestsFailedError,
    UnknownErrorError,
    fail_reasons,
)
from execution_engine.models import ExecuteResult


def _parse_fail_reason(reason: str):
    reason = reason.strip()
    if reason in fail_reasons:
        match reason:
            case "success":
                return
            case "compile":
                raise CompileFailedError
            case "runtime":
                raise RuntimeFailError
            case _:
                raise UnknownErrorError(f"Unknown fail-reason: {reason}")


def _read_file(filename: str) -> str:
    with open(filename) as f:
        return f.read()


def gather_results(config: RunConfig):
    fail_reason: str = _read_file(
        os.path.join(
            config.tmp_dir,
            settings.FAILED_FILE_NAME,
        )
    )

    _parse_fail_reason(fail_reason)

    actual_output: str = _read_file(
        os.path.join(
            config.tmp_dir,
            settings.RUN_STDOUT_FILE_NAME,
        )
    )

    # TODO: Yes, this absolutely shouldn't be in the container,
    #       but I just want something working rn
    expected_output: str = _read_file(
        os.path.join(
            config.tmp_dir,
            settings.EXPECTED_STDOUT_FILE_NAME,
        )
    )

    if actual_output != expected_output:
        raise TestsFailedError

    timing_output: str = _read_file(
        os.path.join(
            config.tmp_dir,
            settings.TIMING_FILE_NAME,
        )
    )

    return ExecuteResult(
        runtime_ms=int(timing_output),  # TODO: Parse values
        mem_usage_mb=int(timing_output),  # TODO: Parse values
        status="success",
        error_msg="",  # No error :)
    )
