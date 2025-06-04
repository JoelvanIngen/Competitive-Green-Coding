from . import file_ops
from execution_engine.src.models.schemas import ExecuteRequest, ExecuteResult
from .docker_manager import DockerManager


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

            _, exit_code = await self._docker_manager.run_container(
                image=IMAGE_NAME,  # TODO: Move to _setup and use Dockerfile instead
                command=["/bin/bash", "/app/run.sh"],
                volumes=volumes,
                working_dir="/app",
                time_limit=time_limit_sec,  # TODO: Pass variable (fixed for all tests?)
                mem_limit_mb=mem_limit_mb,  # TODO: Pass variable (fixed for all tests?)
            )

            # To be continued

        except Exception as e:
            # TODO: Logging
            raise e

        finally:
            if tmp_dir:
                await file_ops.delete_tmp_dir(tmp_dir)
