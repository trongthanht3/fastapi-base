#! /usr/bin/env sh

# Exit in case of error
set -e

TAG=${TAG?Variable not set} \
docker-compose \
-f ./docker/docker-compose.yml \
config > docker-stack.yml

docker-auto-labels docker-stack.yml

docker stack deploy -c docker-stack.yml --with-registry-auth "${STACK_NAME?Variable not set}"
