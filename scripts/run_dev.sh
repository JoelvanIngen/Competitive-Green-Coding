#!/bin/bash

UID=$(id -u)
GID=$(id -g)
export UID
export GID

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
else
    echo "INFO: Starting default compose services"
    if ! docker compose -f compose.yml -f compose.dev.yml up --build --wait -d frontend server_interface execution_engine db_handler; then
        echo "ERROR: Docker compose exited with non-zero exit code";
        exit 1;
    fi
fi

echo "INFO: Started compose services, done."
