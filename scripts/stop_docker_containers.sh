#!/bin/bash

DIRS=(
  "db"
  "execution_engine"
  "server"
  "frontend"
)

# In case the script is called from different folder, finds own folder
OWN_DIR=$(dirname "$(readlink -f "$0")")

PROJECT_ROOT=$(dirname "$OWN_DIR")

echo "DEBUG: PROJECT ROOT: $PROJECT_ROOT"
echo "DEBUG: OWN DIR: $OWN_DIR"
echo "INFO: Stopping compose services"

for dir in "${DIRS[@]}"; do
  SERVICE_PATH="$PROJECT_ROOT/$dir"

  if [[ ! -d "$SERVICE_PATH" ]]; then
    echo "ERROR: Directory '$dir' ($SERVICE_PATH) does not exist"
    exit 1
  fi

  if [[ ! -f "$SERVICE_PATH/compose.yml" ]]; then
    echo "ERROR: No compose.yml found"
    exit 1
  fi

  # Subshell, change directory, run compose and revert
  (
    cd "$SERVICE_PATH" || { echo "ERROR: 'cd' failed"; exit 1; }
    docker compose down  # All this boilerplate just to run this command a few times ._.
    if [[ $? -ne 0 ]]; then
      echo "ERROR: Compose failed on path $SERVICE_PATH";
      exit 1;
    fi
  )

  # Even subshells can fail apparently, check for status
  if [[ $? -ne 0 ]]; then
    echo "ERROR: Subshell failed";
    exit 1;
  fi
done

echo "INFO: Stopped compose services, done."
