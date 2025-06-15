import os
import re
from typing import cast

from execution_engine.config import settings
from execution_engine.docker.runconfig import RunConfig
from execution_engine.errors.errors import (
    CompileFailedError,
    ParseError,
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


def _parse_runtime(s: str) -> tuple[float, int]:
    user_time = None
    max_ram_kbytes = None

    # User time: matches "User time (seconds): " followed by a number with optional decimal
    user_time_pattern = re.compile(r"User time \(seconds\):\s*(\d+\.\d+)")
    # Max RAM: matches "Maximum resident set size (kbytes): " followed by an integer
    max_ram_pattern = re.compile(r"Maximum resident set size \(kbytes\):\s*(\d+)")

    for line in s.splitlines():
        # Try to match user time
        match_user_time = user_time_pattern.match(line)
        if match_user_time:
            try:
                user_time = float(match_user_time.group(1))
            except ValueError:
                print(f"Warning: Could not parse user time from '{match_user_time.group(1)}'")
            continue  # Found it, move to next line

        # Try to match max RAM
        match_max_ram = max_ram_pattern.match(line)
        if match_max_ram:
            try:
                max_ram_kbytes = float(match_max_ram.group(1))  # Convert to float as requested
            except ValueError:
                print(f"Warning: Could not parse max RAM from '{match_max_ram.group(1)}'")
            continue  # Found it, move to next line

    if not user_time or not max_ram_kbytes:
        raise ParseError

    # Make type checker happy now we've established there are no None values
    user_time = cast(float, user_time)
    max_ram_kbytes = cast(int, max_ram_kbytes)

    return user_time, max_ram_kbytes


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

    runtime_sec, mem_usage_kb = _parse_runtime(timing_output)

    return ExecuteResult(
        runtime_ms=int(runtime_sec * 1_000),
        mem_usage_mb=int(mem_usage_kb / 1_000),
        status="success",
        error_msg="",  # No error :)
    )
