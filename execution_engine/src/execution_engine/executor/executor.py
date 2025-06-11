"""
Module that receives the execution request.
Creates config and requests scheduling
"""

from execution_engine.docker.gather import gather_results
from execution_engine.docker.languages import language_info
from execution_engine.docker.prepare import setup_env
from execution_engine.docker.runconfig import RunConfig
from execution_engine.executor.scheduler import schedule_run
from execution_engine.models import ExecuteRequest


async def entry(request: ExecuteRequest):
    config = RunConfig(
        tmp_dir="",  # Will be filled in at prepare
        cpu=0,  # Will be filled in at scheduler
        language=language_info[request.language],
        origin_request=request,
    )

    await setup_env(config, request.code)
    await schedule_run(config)
    await gather_results(config)
