#!/bin/bash

docker compose down
docker volume rm competitive-green-coding_postgres competitive-green-coding_node_modules_cache competitive-green-coding_storage
