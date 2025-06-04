import asyncio
import enum
from unittest import case

import docker
from docker.errors import APIError
from docker.types import Ulimit
from loguru import logger

from execution_engine.src.config import MAX_NPROC, MAX_FSIZE, TIME_LIMIT_SEC, MEM_LIMIT_MB, IMAGE_NAME
from execution_engine.src.models.schemas import status_t


class DockerStatus(enum.Enum):
    success = "success"
    timeout = "timeout"
    mem_limit_exceeded = "mem_limit_exceeded"
    internal_error = "internal_error"

    def to_status_t(self) -> status_t:
        match self:
            case self.timeout:
                return "timeout"
            case self.mem_limit_exceeded:
                return "mem_limit_exceeded"
            case self.internal_error:
                return "internal_error"
            case self.success:
                return "success"
            case _:
                # Not possible
                return "internal_error"



class DockerManager:
    """
    Class for all Docker-related logic
    """
    def __init__(self):
        self._client = docker.from_env()
        logger.info("Docker client initialised from environment")

    @staticmethod
    async def _run_blocking_op(func, *args, **kwargs):
        """
        Creates a new thread for an operation to avoid blocking the main thread
        """
        try:
            return await asyncio.to_thread(func, *args, **kwargs)
        except APIError as e:
            logger.error(f"Docker API error during blocking operation '{func.__name__}': {e}")
            raise  # TODO: Gracefully recover
        except Exception as e:
            logger.error(f"Unexpected error during blocking operation '{func.__name__}': {e}")
            raise  # TODO: Gracefully recover

    async def pull_image(self, image_name: str):
        """
        Pulls an image if not available
        """
        try:
            logger.info(f"Pulling image '{image_name}'")
            await self._run_blocking_op(self._client.images.pull, image_name)
            logger.info(f"Image '{image_name}' successfully pulled")
        except APIError as e:
            logger.error(f"Docker API error pulling image '{image_name}': {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error pulling image '{image_name}'")
            raise

    async def build_image(self, path: str, dockerfile: str = 'Dockerfile') -> str:
        try:
            logger.info(f"Building image '{path}'")
            # We deliberately wait here; we don't want to start anything else before we're ready
            image, build_logs_generator = await self._client.images.build(
                path=path,
                dockerfile=dockerfile,
                tag=IMAGE_NAME
            )
            logger.info(f"Image '{path}' successfully built")
            return image
        except APIError as e:
            logger.error(f"Docker API error building image '{path}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error building image '{path}': {e}")
            raise

    async def run_container(self,
                            image: str,
                            command: list[str],
                            volumes: dict[str, dict[str, str]],
                            working_dir: str) -> DockerStatus:
        """
        Runs a docker container with specified params and resource limits
        :returns: raw logs and exit code
        """
        ulimits = [
            Ulimit(name='nproc', soft=MAX_NPROC, hard=MAX_NPROC),
            Ulimit(name='fsize', soft=MAX_FSIZE, hard=MAX_FSIZE),
        ]

        try:
            # TODO: Check if all these options are correct, it's 1am and I can't be bothered rn
            container = await self._run_blocking_op(
                self._client.containers.run,
                image=IMAGE_NAME,
                command=command,
                volumes=volumes,
                working_dir=working_dir,
                remove=True,  # Remove container on exit
                detach=True,  # Don't wait for container to finish
                network_mode=None,  # Don't allow network access
                mem_limit=f'{MEM_LIMIT_MB}m',
                ulimits=ulimits,
                cpuset_cpus=0,  # Pin to specific CPU core
                                # TODO: Make dynamic when implementing execution scheduler
                security_opt=["no-new-privileges:true"],  # Security
                cap_drop=["ALL"],  # Security
                read_only=True,
                user="nobody",  # Non-root user
            )
            logger.info(f"Container '{container.id[:12]}' started")

            # Timeout handling
            # TODO: duplicate timeout handling in here + in run.sh, maybe choose one?
            try:
                with asyncio.timeout(TIME_LIMIT_SEC):
                    logger.debug(f"Waiting for container '{container.id[:12]}' to finish (max {TIME_LIMIT_SEC}s)...")
                    result = await container.wait()
                    exit_code = result["StatusCode"]
                    logger.debug(f"Container '{container.id[:12]}' finished with exit code: {exit_code}")
                    return DockerStatus.success

            except asyncio.TimeoutError:
                logger.warning(f"Container '{container.id[:12]}' timed out")
                await self._run_blocking_op(container.kill)
                return DockerStatus.timeout

        except APIError as e:
            logger.error(f"Docker API error running container '{image}': {e}")
            return DockerStatus.internal_error
        except Exception as e:
            logger.error(f"Unexpected error running container '{image}': {e}")
            return DockerStatus.internal_error

        # TODO: Return something useful
