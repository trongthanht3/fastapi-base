#! /usr/bin/env sh

# Exit in case of error
set -e

TAG=${TAG?Variable not set} \
sh ./docker/scripts/build.sh

docker-compose -f ./docker/docker-compose.yml push
