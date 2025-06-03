from typing import TextIO

from execution_engine.src.models.schemas import ExecuteRequest, ExecuteResult


class Executor:
    def __init__(self):
        self._docker_manager = DockerManager()  # TODO: Implement
        self._file_manager = FileManager()  # TODO: Implement

        self.input_file = "input.txt"  # Might not be necessary if we do decide to hardcode tests
        self.stdout_file = "stdout.txt"
        self.stderr_file = "stderr.txt"
        self.time_stats_file = "time_stats.txt"

    async def _setup_environment(self, tmp_dir: TextIO):
        raise NotImplementedError()

    async def execute_code(self, request: ExecuteRequest) -> ExecuteResult:
        raise NotImplementedError()
