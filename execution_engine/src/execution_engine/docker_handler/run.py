import asyncio
import os

from docker.types import Ulimit
from loguru import logger

from execution_engine.config import settings
from execution_engine.docker_handler.runconfig import RunConfig
from execution_engine.errors import CpuOutOfRangeError

from ..errors.errors import ContainerOOMError
from .state import client, host_gid, host_uid

_ulimits = [
    Ulimit(
        name="nproc",
        soft=settings.EXECUTION_ENVIRONMENT_MAX_NPROC,
        hard=settings.EXECUTION_ENVIRONMENT_MAX_NPROC,
    ),
    Ulimit(
        name="fsize",
        soft=settings.EXECUTION_ENVIRONMENT_MAX_FSIZE,
        hard=settings.EXECUTION_ENVIRONMENT_MAX_FSIZE,
    ),
]

_cpu_count = os.cpu_count()


def _validate_cpu(cpu: int) -> None:
    """
    Confirms the listed CPU exists on the system, and raises otherwise
    """
    if _cpu_count is None:
        raise CpuOutOfRangeError("Could not determine number of CPUs")

    if cpu >= _cpu_count or cpu < 0:
        raise CpuOutOfRangeError(f"CPU out of range: {cpu}")


def _run_and_wait_container(config: RunConfig):
    volumes = {config.tmp_dir: {"bind": "/app", "mode": "rw"}}
    logger.info("Starting container")
    container = client.containers.run(
        image=config.language.image,
        volumes=volumes,
        remove=True,  # Remove container on exit
        detach=True,  # Don't wait for container to finish
        network_mode=None,  # Don't allow network access
        mem_limit=f"{settings.MEM_LIMIT_MB}m",
        ulimits=_ulimits,
        cpuset_cpus=str(config.cpu),  # Pin to specific CPU core
        security_opt=["no-new-privileges:true"],  # Security
        cap_drop=["ALL"],  # Security
        read_only=True,
        user=f"{host_uid}:{host_gid}",  # Non-root user
    )
    logger.info(f"Container '{container.id}' started")

    res = container.wait()

    # Catch OOM and raise
    if res["StatusCode"] == 137:
        raise ContainerOOMError


async def run(config: RunConfig) -> None:
    """
    Runs the Docker container. On function exit, the container will either have finished running
    or will have crashed.
    :returns: Container
    :raises CpuOutOfRangeError: if CPU number does not exist on host system
    :raises asyncio.TimeoutError: if container took too long
    :raises docker.APIError: if Docker ran into problems
    """
    async with asyncio.timeout(settings.TIME_LIMIT_SEC):
        return await asyncio.to_thread(_run_and_wait_container, config)
