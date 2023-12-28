#! /usr/bin/env sh

# Exit in case of error
set -e

TAG=${TAG?Variable not set} \

(echo -e "version: '3.9'\n";  docker compose -f docker-compose.yml config) > docker-stack.yml

docker stack deploy -c docker-stack.yml --with-registry-auth "${STACK_NAME?Variable not set}"