import asyncio
import os

from docker.models.containers import Container
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


def _save_logs(container: Container, path: str) -> None:
    logs = container.logs().decode()
    with open(os.path.join(path, "container_logs.log"), "w") as f:
        f.write(logs)


def _run_and_wait_container(config: RunConfig):
    basename = os.path.basename(config.tmp_dir)
    workdir_in_container = os.path.join("/app", basename)

    volumes = {"competitive-green-coding_runtimes_data": {"bind": "/app", "mode": "rw", "subpath": os.path.basename(config.tmp_dir)}}
    logger.info(f"Worker {config.cpu} : Starting container with working directory {config.tmp_dir}\n"
                f"Path in container: {workdir_in_container}")

    container = client.containers.run(
        image=config.language.image,
        volumes=volumes,
        working_dir=workdir_in_container,
        remove=False,  # Don't remove container on exit (we want to acces logs)
        detach=True,  # Don't wait for container to finish
        network_mode=None,  # Don't allow network access
        mem_limit=f"{settings.MEM_LIMIT_MB}m",
        ulimits=_ulimits,
        cpuset_cpus=str(config.cpu),  # Pin to specific CPU core
        security_opt=["no-new-privileges:true"],  # Security
        cap_drop=["ALL"],  # Security
        read_only=True,
        user=f"{host_uid}:{host_gid}",  # Non-root user
        entrypoint="./run.sh",
    )
    logger.info(f"Worker {config.cpu} : Container '{container.id}' started")

    try:
        res = container.wait()
        _save_logs(container, config.tmp_dir)
    finally:
        container.remove(force=True)

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
    :raises ContainerOOMError: if container out of maximum allowed memory
    """
    async with asyncio.timeout(settings.TIME_LIMIT_SEC):
        return await asyncio.to_thread(_run_and_wait_container, config)
