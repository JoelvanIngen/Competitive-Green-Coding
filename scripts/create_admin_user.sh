#!/bin/bash

if ! docker exec db_handler python -m aux.admin_populator
then
  echo "ERROR: Docker compose exited with non-zero exit code";
  exit 1;
fi

echo "INFO: Created admin user, done."
