#!/bin/bash

if ! docker exec db_handler python -m scripts.leaderboard_populator.py
then
  echo "ERROR: Docker compose exited with non-zero exit code";
  exit 1;
fi

echo "INFO: Populated db with users, a problem and submissions."
