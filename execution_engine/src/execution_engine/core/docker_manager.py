import asyncio
import enum

import docker
from docker.errors import APIError
from docker.types import Ulimit
from loguru import logger

from execution_engine.config import settings
from execution_engine.models import StatusType


class DockerStatus(enum.Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    MEM_LIMIT_EXCEEDED = "mem_limit_exceeded"
    INTERNAL_ERROR = "internal_error"

    def to_status_t(self) -> StatusType:
        match self:
            case self.TIMEOUT:
                return "timeout"
            case self.MEM_LIMIT_EXCEEDED:
                return "mem_limit_exceeded"
            case self.INTERNAL_ERROR:
                return "internal_error"
            case self.SUCCESS:
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

        logger.info("Building Docker images...")
        # Hardcoded C for now
        self.build_image("execution_env/C", "Dockerfile")
        logger.info("Built Docker images")

    @staticmethod
    async def _run_blocking_op(func, *args, **kwargs):
        """
        Creates a new thread for an operation to avoid blocking the main thread
        """

        try:
            return await asyncio.to_thread(func, *args, **kwargs)
        except APIError as e:
            logger.error(f"Docker API error during blocking operation " f"'{func.__name__}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during blocking operation " f"'{func.__name__}': {e}")
            raise

    async def build_image(self, path: str, dockerfile: str = "Dockerfile"):
        """
        Builds an image from a Dockerfile. Returns the resulting image
        """

        try:
            logger.info(f"Building image '{path}'")
            # We deliberately wait here; we don't want to start anything else
            # before we're ready
            image, _ = self._client.images.build(
                path=path, dockerfile=dockerfile, tag=settings.EXECUTION_ENVIRONMENT_IMAGE_NAME
            )
            logger.info(f"Image '{path}' successfully built")
            return image
        except APIError as e:
            logger.error(f"Docker API error building image '{path}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error building image '{path}': {e}")
            raise

    async def run_container(
        self, image: str, command: list[str], volumes: dict[str, dict[str, str]], working_dir: str
    ) -> DockerStatus:
        """
        Runs a docker container with specified params and resource limits
        :returns: raw logs and exit code
        """
        ulimits = [
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

        try:
            container = await self._run_blocking_op(
                self._client.containers.run,
                image=settings.EXECUTION_ENVIRONMENT_IMAGE_NAME,
                command=command,
                volumes=volumes,
                working_dir=working_dir,
                remove=True,  # Remove container on exit
                detach=True,  # Don't wait for container to finish
                network_mode=None,  # Don't allow network access
                mem_limit=f"{settings.MEM_LIMIT_MB}m",
                ulimits=ulimits,
                # Pin to specific CPU core
                # Will be made dynamic (each core one worker) when we implement scheduler
                cpuset_cpus=0,
                security_opt=["no-new-privileges:true"],  # Security
                cap_drop=["ALL"],  # Security
                read_only=True,
                user="nobody",  # Non-root user
            )
            logger.info(f"Container '{container.id[:12]}' started")

            # Timeout handling
            try:
                async with asyncio.timeout(settings.TIME_LIMIT_SEC):
                    logger.debug(
                        f"Waiting for container '{container.id[:12]}'"
                        f" to finish (max {settings.TIME_LIMIT_SEC}s)..."
                    )
                    result = await container.wait()
                    exit_code = result["StatusCode"]
                    logger.debug(
                        f"Container '{container.id[:12]}' finished" f" with exit code: {exit_code}"
                    )
                    return DockerStatus.SUCCESS

            except asyncio.TimeoutError:
                logger.warning(f"Container '{container.id[:12]}' timed out")
                await self._run_blocking_op(container.kill)
                return DockerStatus.TIMEOUT

        except APIError as e:
            logger.error(f"Docker API error running container '{image}': {e}")
            return DockerStatus.INTERNAL_ERROR
        except Exception as e:
            logger.error(f"Unexpected error running container '{image}': {e}")
            raise  # DockerStatus.INTERNAL_ERROR
