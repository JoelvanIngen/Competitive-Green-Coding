import asyncio
from asyncio import timeout

import docker
from docker.types import Ulimit


class DockerManager:
    """
    Class for all Docker-related logic
    """
    def __init__(self):
        self._client = docker.from_env()

    @staticmethod
    async def _run_blocking_op(func, *args, **kwargs):
        """
        Creates a new thread for an operation to avoid blocking the main thread
        """
        try:
            return await asyncio.to_thread(func, *args, **kwargs)
        except Exception as e:
            # TODO: Logging
            raise e

    async def pull_image(self, image_name: str):
        """
        Pulls an image if not available
        """
        try:
            await self._run_blocking_op(self._client.images.pull, image_name)
        except Exception as e:
            # TODO: Logging
            raise e

    async def run_container(self,
                            image: str,
                            command: list[str],
                            volumes: dict[str, dict[str, str]],
                            working_dir: str,
                            time_limit: int,
                            mem_limit_mb: int, ):
        """
        Runs a docker container with specified params and resource limits
        :returns: raw logs and exit code
        """
        ulimits = [
            Ulimit(name='nproc', soft=MAX_NPROC, hard=MAX_NPROC),
            Ulimit(name='fsize', soft=MAX_FSIZE, hard=MAX_FSIZE),
        ]

        # TODO: Check if all these options are correct, it's 1am and I can't be bothered rn
        container = await self._run_blocking_op(
            self._client.containers.run,
            image=image,
            command=command,
            volumes=volumes,
            working_dir=working_dir,
            remove=True,  # Remove container on exit
            detach=False,  # Wait for container to finish
            network_mode=None,  # Don't allow network access
            mem_limit=f'{mem_limit_mb}m',
            ulimits=ulimits,
            cpuset_cpus=0,  # Pin to specific CPU core
                            # TODO: Make dynamic when implementing execution scheduler
            security_opt=["no-new-privileges:true"],  # Security
            cap_drop=["ALL"],  # Security
            read_only=True,
            user="nobody",  # Non-root user
            timeout=time_limit,
        )
