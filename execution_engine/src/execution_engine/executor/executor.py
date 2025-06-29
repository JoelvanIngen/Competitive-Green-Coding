"""
Module that receives the execution request.
Creates config and requests scheduling
"""

import asyncio
import traceback

import docker.errors  # pylint: disable=import-error, no-name-in-module
from loguru import logger

from common.languages import language_info
from common.schemas import SubmissionCreate, SubmissionResult
from common.typing import ErrorReason
from execution_engine.docker_handler.clean import clean_env
from execution_engine.docker_handler.gather import gather_results
from execution_engine.docker_handler.prepare import setup_env
from execution_engine.docker_handler.runconfig import RunConfig
from execution_engine.errors.errors import (
    CompileFailedError,
    ContainerOOMError,
    RuntimeFailError,
    TestsFailedError,
)
from execution_engine.executor.communication import result_to_db
from execution_engine.executor.scheduler import schedule_run


async def entry(request: SubmissionCreate):
    try:
        # If any error occurs here, we log and do nothing

        config = RunConfig(
            tmp_dir="",  # Will be filled in at prepare
            cpu=0,  # Will be filled in at scheduler
            language=language_info[request.language],
            origin_request=request,
        )

    except Exception as e:
        logger.error(f"Exception during config creation: {e}", exc_info=True)
        raise

    # This WILL get overwritten, but creating a "internal error" dummy result here to satisfy
    # type checker
    res = SubmissionResult(
        submission_uuid=request.submission_uuid,
        runtime_ms=0.00,
        emissions_kg=0.0,
        energy_usage_kwh=0.0,
        successful=False,
        error_reason=ErrorReason.INTERNAL_ERROR,
        error_msg="",
    )

    try:
        await setup_env(config, request.code)
        await schedule_run(config)

        # Disable pylint until we actually use emissons_co2 variable
        runtime_s, energy_kwh, emissions_co2 = gather_results(config)  # pylint: disable=W0612

        res = SubmissionResult(
            submission_uuid=request.submission_uuid,
            runtime_ms=runtime_s * 1000,
            emissions_kg=emissions_co2,
            energy_usage_kwh=energy_kwh,
            successful=True,
            error_reason=None,
            error_msg="",
        )

    except TestsFailedError as e:
        res = SubmissionResult(
            submission_uuid=request.submission_uuid,
            runtime_ms=0.00,
            emissions_kg=0.0,
            energy_usage_kwh=0.0,
            successful=False,
            error_reason=ErrorReason.TESTS_FAILED,
            error_msg=e.msg,
        )

    except CompileFailedError as e:
        res = SubmissionResult(
            submission_uuid=request.submission_uuid,
            runtime_ms=0.00,
            emissions_kg=0.0,
            energy_usage_kwh=0.0,
            successful=False,
            error_reason=ErrorReason.COMPILE_ERROR,
            error_msg=e.msg,
        )

    except RuntimeFailError as e:
        res = SubmissionResult(
            submission_uuid=request.submission_uuid,
            runtime_ms=0.00,
            emissions_kg=0.0,
            energy_usage_kwh=0.0,
            successful=False,
            error_reason=ErrorReason.RUNTIME_ERROR,
            error_msg=e.msg,
        )

    except asyncio.TimeoutError:
        res = SubmissionResult(
            submission_uuid=request.submission_uuid,
            runtime_ms=0.00,
            emissions_kg=0.0,
            energy_usage_kwh=0.0,
            successful=False,
            error_reason=ErrorReason.TIMEOUT,
            error_msg="",
        )

    except ContainerOOMError:
        res = SubmissionResult(
            submission_uuid=request.submission_uuid,
            runtime_ms=0,
            emissions_kg=0.0,
            energy_usage_kwh=0.0,
            successful=False,
            error_reason=ErrorReason.MEM_LIMIT,
            error_msg="",  # Can be parsed front-end
        )

    except (docker.errors.APIError, Exception) as e:  # pylint: disable=W0718, I1101
        logger.error(f"Exception during execution: {e}", exc_info=True)
        logger.error(f"Traceback: {traceback.format_exc()}")

        res = SubmissionResult(
            submission_uuid=request.submission_uuid,
            runtime_ms=0.00,
            emissions_kg=0.0,
            energy_usage_kwh=0.0,
            successful=False,
            error_reason=ErrorReason.INTERNAL_ERROR,
            error_msg="",  # Internal error _is_ the error; can be parsed front-end
        )

    finally:
        await result_to_db(res)

        clean_env(config)
