#!/bin/bash

# Detect user uid/gid
HOST_USER_UID=$(id -u)
export HOST_USER_UID

# Detect docker group id, depending on the OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS with Docker Desktop - use default GID
    HOST_DOCKER_GID=999
else
    # Linux - try to get actual docker group GID
    HOST_DOCKER_GID=$(getent group docker | cut -d: -f3 2>/dev/null)
fi
export HOST_DOCKER_GID

echo "DEBUG: DOCKER GID: $HOST_DOCKER_GID"

# In case the script is called from different folder, finds own folder
OWN_DIR=$(dirname "$(readlink -f "$0")")

PROJECT_ROOT=$(dirname "$OWN_DIR")

echo "DEBUG: PROJECT ROOT: $PROJECT_ROOT"
echo "DEBUG: OWN DIR: $OWN_DIR"
echo "INFO: Starting compose services"

cd "$PROJECT_ROOT" || { echo "ERROR: 'cd' failed"; exit 1; }

# Check if specific services are provided as arguments
if [ $# -gt 0 ]; then
    echo "INFO: Starting specific compose services: $*"
    if ! docker compose -f compose.yml -f compose.dev.yml up --build --wait -d "$@"; then
        echo "ERROR: Docker compose exited with non-zero exit code";
        exit 1;
    fi

# Default: start all services
else
    echo "INFO: Starting default compose services"
    if ! docker compose -f compose.yml -f compose.dev.yml up --build --wait -d frontend server_interface execution_engine db_handler; then
        echo "ERROR: Docker compose exited with non-zero exit code";
        exit 1;
    fi
fi

echo "INFO: Started compose services, done."
