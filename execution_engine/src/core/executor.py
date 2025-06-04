from . import async_file_ops
from execution_engine.src.models.schemas import ExecuteRequest, ExecuteResult
from .docker_manager import DockerManager
from ..config import CONTAINER_SCRIPT, CONTAINER_APP_DIR


class Executor:
    def __init__(self):
        self._docker_manager = DockerManager()

    async def _setup_environment(self, tmp_dir: str):
        raise NotImplementedError()

    async def execute_code(self, request: ExecuteRequest) -> ExecuteResult:
        tmp_dir = None

        try:
            tmp_dir = await file_ops.create_tmp_dir()

            await self._setup_environment(tmp_dir)

            volumes = {tmp_dir: {"bind": "/app", "mode": "rw"}}

            exit_code = await self._docker_manager.run_container(
                image=IMAGE_NAME,  # TODO: Move to _setup and use Dockerfile instead
                command=["/bin/bash", CONTAINER_SCRIPT],
                volumes=volumes,
                working_dir=CONTAINER_APP_DIR,
            )

            # To be continued

        except Exception as e:
            # TODO: Logging
            raise e

        finally:
            await async_file_ops.delete_tmp_dir(tmp_dir)
