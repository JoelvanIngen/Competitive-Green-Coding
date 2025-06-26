#!/bin/bash

# Detect user uid
HOST_USER_UID=$(id -u)
export HOST_USER_UID

# Detect docker gid
HOST_DOCKER_GID=$(getent group docker | cut -d: -f3 2>/dev/null)
export HOST_DOCKER_GID

# In case the script is called from different folder, finds own folder
OWN_DIR=$(dirname "$(readlink -f "$0")")

PROJECT_ROOT=$(dirname "$OWN_DIR")

echo "DEBUG: PROJECT ROOT: $PROJECT_ROOT"
echo "DEBUG: OWN DIR: $OWN_DIR"
echo "INFO: Starting compose services"

cd "$PROJECT_ROOT" || { echo "ERROR: 'cd' failed"; exit 1; }

if ! docker compose up --build -d
then
  echo "ERROR: Docker compose exited with non-zero exit code";
  exit 1;
fi

echo "INFO: Started compose services, done."
