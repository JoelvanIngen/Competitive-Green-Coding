"""
Module that receives the execution request.
Creates config and requests scheduling
"""

import asyncio

import docker.errors
from loguru import logger

from execution_engine.docker.clean import clean_env
from execution_engine.docker.gather import gather_results
from execution_engine.docker.languages import language_info
from execution_engine.docker.prepare import setup_env
from execution_engine.docker.runconfig import RunConfig
from execution_engine.errors.errors import CompileFailedError, RuntimeFailError, TestsFailedError
from execution_engine.executor.communication import result_to_db
from execution_engine.executor.scheduler import schedule_run
from execution_engine.models import ExecuteRequest, ExecuteResult


async def entry(request: ExecuteRequest):
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
    res = ExecuteResult(
        runtime_ms=0,
        mem_usage_mb=0,
        status="internal_error",
        error_msg="",
    )

    try:
        await setup_env(config, request.code)
        await schedule_run(config)
        res = await gather_results(config)

    except TestsFailedError:
        res = ExecuteResult(
            runtime_ms=0,
            mem_usage_mb=0,
            status="failed",
            error_msg="",  # TODO: Put something useful here
        )

    except CompileFailedError:
        res = ExecuteResult(
            runtime_ms=0,
            mem_usage_mb=0,
            status="compile_error",
            error_msg="",  # TODO: Put something useful here
        )

    except RuntimeFailError:
        res = ExecuteResult(
            runtime_ms=0,
            mem_usage_mb=0,
            status="runtime_error",
            error_msg="",  # TODO: Put something useful here
        )

    except asyncio.TimeoutError:
        res = ExecuteResult(
            runtime_ms=0,
            mem_usage_mb=0,
            status="timeout",
            error_msg="",  # Timeout _is_ the error; can be parsed front-end
        )

    except (docker.errors.APIError, Exception) as e:  # pylint: disable=W0718
        logger.error(f"Exception during execution: {e}", exc_info=True)

        res = ExecuteResult(
            runtime_ms=0,
            mem_usage_mb=0,
            status="internal_error",
            error_msg="",  # Internal error _is_ the error; can be parsed front-end
        )

    # TODO: Catch OOM error if container uses too much RAM

    finally:
        await result_to_db(res)

        clean_env(config)
