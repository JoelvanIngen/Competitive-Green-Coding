#!/bin/bash

# Stop all containers
source stop_docker_containers.sh

# Delete all images
docker image rm server-server db-db_handler execution_engine-execution_engine