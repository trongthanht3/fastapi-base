#! /usr/bin/env sh

# Exit in case of error
set -e

[ ! -f ./.env ] || export $(grep -v '^#' ./.env | xargs)

TAG=${TAG?Variable not set} \
sh ./docker/scripts/build.sh

#docker-compose -f ./docker-compose.yml push
echo "test scripts"
echo $TAG

docker-compose push backend celeryworker celeryflower
