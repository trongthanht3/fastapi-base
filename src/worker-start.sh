#! /usr/bin/env bash
set -e

python /app/celeryworker_pre_start.py

celery -A celeryApp.worker worker -l info -Q main-queue -c 1 -E
