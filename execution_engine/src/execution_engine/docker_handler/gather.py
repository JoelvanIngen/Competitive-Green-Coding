import os
import re
from typing import cast

from loguru import logger

from execution_engine.config import settings
from execution_engine.docker_handler.runconfig import RunConfig
from execution_engine.errors.errors import (
    CompileFailedError,
    ParseError,
    RuntimeFailError,
    UnknownErrorError,
)
from execution_engine.parsers import codecarbon
from execution_engine.parsers.grader import grader


def _report_compile_err(config: RunConfig):
    compile_err = _read_file(os.path.join(config.tmp_dir, settings.COMPILE_STDERR_FILE_NAME))

    raise CompileFailedError(compile_err)


def _report_runtime_error(config: RunConfig):
    runtime_err = _read_file(os.path.join(config.tmp_dir, settings.RUN_STDERR_FILE_NAME))

    raise RuntimeFailError(runtime_err)


def _parse_fail_reason(config: RunConfig, reason: str):
    reason = reason.strip()
    match reason:
        case "success":
            return
        case "compile":
            _report_compile_err(config)
        case "runtime":
            _report_runtime_error(config)
        case _:
            raise UnknownErrorError(f"Unknown fail-reason: {reason}")


def _parse_runtime(s: str) -> tuple[float, float, float]:
    user_time: float | None = None
    max_ram_kbytes: float | None = None
    energy_kwh: float | None = None

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
            except ValueError as e:
                logger.error(f"Could not parse user time from '{match_user_time.group(1)}'")
                raise UnknownErrorError from e

        # Try to match max RAM
        match_max_ram = max_ram_pattern.search(line)
        if match_max_ram:
            try:
                max_ram_kbytes = int(match_max_ram.group(1))
            except ValueError as e:
                logger.error(f"Could not parse max RAM from '{match_max_ram.group(1)}'")
                raise UnknownErrorError from e

    if user_time is None or max_ram_kbytes is None:
        raise ParseError

    # Make type checker happy now we've established there are no None values
    user_time = cast(float, user_time)
    max_ram_kbytes = cast(float, max_ram_kbytes)
    energy_kwh = cast(float, energy_kwh)

    return user_time, max_ram_kbytes, energy_kwh


def _read_file(filename: str) -> str:
    with open(filename) as f:
        return f.read()


def _calc_emissions(measurement):
    duration, emissions, energy = measurement
    # Divide by 1000 since we do 1000 runs
    return (
        duration / 1000,
        energy / 1000,
        emissions / 1000,
    )


def gather_results(config: RunConfig) -> tuple[float, float, float]:
    """
    Retrieves and returns a tuple of
    - Runtime per run in seconds
    - Energy usage per run in kwh
    - Emissions per run in kg CO2
    """
    fail_reason: str = _read_file(
        os.path.join(
            config.tmp_dir,
            settings.FAILED_FILE_NAME,
        )
    )

    _parse_fail_reason(config, fail_reason)

    inputs: str = _read_file(
        os.path.join(
            config.tmp_dir,
            settings.INPUTS_FILE_NAME,
        )
    )

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

    grader(inputs, expected_output, actual_output)

    emissions = codecarbon.parse(
        os.path.join(
            config.tmp_dir,
            settings.EMISSIONS_OUTPUT_FILE_NAME,
        )
    )

    runtime_s, energy_kwh, co2 = _calc_emissions(emissions)

    return runtime_s, energy_kwh, co2
