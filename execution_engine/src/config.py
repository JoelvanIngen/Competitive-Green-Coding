import os

HOST = "127.0.0.1"
PORT = 8081

# Resource limits
MAX_NPROC = 100
MAX_FSIZE = 1_024_000  # 1 mb max for created files

CONTAINER_APP_DIR = '/app'
SCRIPT_NAME = 'run.sh'
CONTAINER_SCRIPT = os.path.join(CONTAINER_APP_DIR, SCRIPT_NAME)

INPUT_FILE_NAME = "input.txt"
STDOUT_FILE_NAME = "stdout.txt"
STDERR_FILE_NAME = "stderr.txt"

TIME_LIMIT_SEC = 10
MEM_LIMIT_MB = 1024  # Which is very generous, we could lower this

TEMP_DIR_PREFIX = 'execution_run_'
