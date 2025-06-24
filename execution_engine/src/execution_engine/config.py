import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Reads environment variables from the environment. If a variable is not found, the default
    value is used as defined here.

    WARNING: These are defaults, only used locally and overwritten in production. If you want to
    change anything here, you should also change .env.example
    """

    USING_ENV_FILE: int = 0

    # Execution engine settings
    EXECUTION_ENGINE_HOST: str = "0.0.0.0"
    EXECUTION_ENGINE_PORT: int = 8080

    # DB handler settings
    DB_HANDLER_HOST: str = "db"
    DB_HANDLER_PORT: int = 8080

    DB_HANDLER_URL: str = f"http://{DB_HANDLER_HOST}:{DB_HANDLER_PORT}"

    # Resource limits
    EXECUTION_ENVIRONMENT_MAX_NPROC: int = 1000
    EXECUTION_ENVIRONMENT_MAX_FSIZE: int = 1024000

    EXECUTION_ENVIRONMENT_IMAGE_NAME: str = "c_execution_image"
    EXECUTION_ENVIRONMENT_APP_DIR: str = "/app"
    EXECUTION_ENVIRONMENT_SCRIPT_NAME: str = "run.sh"
    CONTAINER_SCRIPT: str = os.path.join(
        EXECUTION_ENVIRONMENT_APP_DIR, EXECUTION_ENVIRONMENT_SCRIPT_NAME
    )
    EXECUTION_ENVIRONMENT_TMP_DIR_PREFIX: str = "execution_run_"

    TMP_DIR_PATH_BASE: str = "/runtimes"

    INPUTS_FILE_NAME: str = "inputs.txt"
    COMPILE_STDOUT_FILE_NAME: str = "compile_stdout.txt"
    COMPILE_STDERR_FILE_NAME: str = "compile_stderr.txt"
    EXPECTED_STDOUT_FILE_NAME: str = "expected_output.txt"
    RUN_STDOUT_FILE_NAME: str = "actual_output.txt"
    RUN_STDERR_FILE_NAME: str = "stderrs.txt"
    FAILED_FILE_NAME: str = "failed.txt"
    TIMING_FILE_NAME: str = "timing.txt"

    TIME_LIMIT_SEC: int = 10
    MEM_LIMIT_MB: int = 512  # Which is very generous, we could lower this


settings = Settings()

if settings.USING_ENV_FILE:
    # We want to force localhost if running locally
    # Without this; EXECUTION_ENGINE_HOST resolves to 'execution_engine', which won't run locally
    settings.EXECUTION_ENGINE_HOST = "127.0.0.1"  # pylint: disable=C0103
