import os
import re
from typing import cast

from loguru import logger

from execution_engine.config import settings
from execution_engine.docker.runconfig import RunConfig
from execution_engine.errors.errors import (
    CompileFailedError,
    ParseError,
    RuntimeFailError,
    TestsFailedError,
    UnknownErrorError,
)


def _parse_fail_reason(reason: str):
    reason = reason.strip()
    match reason:
        case "success":
            return
        case "compile":
            raise CompileFailedError
        case "runtime":
            raise RuntimeFailError
        case _:
            raise UnknownErrorError(f"Unknown fail-reason: {reason}")


def _parse_runtime(s: str) -> tuple[float, int]:
    user_time: float | None = None
    max_ram_kbytes: int | None = None

    # User time: matches "User time (seconds): " followed by a number with optional decimal
    user_time_pattern = re.compile(r"User time \(seconds\):\s*(\d+\.\d+)")
    # Max RAM: matches "Maximum resident set size (kbytes): " followed by an integer
    max_ram_pattern = re.compile(r"Maximum resident set size \(kbytes\):\s*(\d+)")

    for line in s.splitlines():
        # Try to match user time
        match_user_time = user_time_pattern.search(line)
        if match_user_time:
            try:
                user_time = float(match_user_time.group(1))
            except ValueError:
                logger.error(f"Could not parse user time from '{match_user_time.group(1)}'")
                raise UnknownErrorError

        # Try to match max RAM
        match_max_ram = max_ram_pattern.search(line)
        if match_max_ram:
            try:
                max_ram_kbytes = int(match_max_ram.group(1))
            except ValueError:
                logger.error(f"Could not parse max RAM from '{match_max_ram.group(1)}'")
                raise UnknownErrorError

    if user_time is None or max_ram_kbytes is None:
        raise ParseError

    # Make type checker happy now we've established there are no None values
    user_time = cast(float, user_time)
    max_ram_kbytes = cast(int, max_ram_kbytes)

    return user_time, max_ram_kbytes


def _read_file(filename: str) -> str:
    with open(filename) as f:
        return f.read()


def gather_results(config: RunConfig) -> tuple[int, float]:
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

    user_time_s, max_ram_kbytes = _parse_runtime(timing_output)

    return int(user_time_s * 1000), max_ram_kbytes / 1000
