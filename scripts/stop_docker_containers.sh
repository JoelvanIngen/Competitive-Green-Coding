#!/bin/bash

# In case the script is called from different folder, finds own folder
OWN_DIR=$(dirname "$(readlink -f "$0")")

PROJECT_ROOT=$(dirname "$OWN_DIR")

echo "DEBUG: PROJECT ROOT: $PROJECT_ROOT"
echo "DEBUG: OWN DIR: $OWN_DIR"
echo "INFO: Stopping compose services"

cd "$PROJECT_ROOT" || { echo "ERROR: 'cd' failed"; exit 1; }

if ! docker compose down
then
  echo "ERROR: Docker compose exited with non-zero exit code";
  exit 1;
fi

echo "INFO: Stopped compose services, done."
