#!/bin/bash

if ! docker exec db_handler python -m scripts.leaderboard_populator
then
  echo "ERROR: Docker compose exited with non-zero exit code";
  exit 1;
fi

echo "INFO: Populated db with users, problems and submissions."
