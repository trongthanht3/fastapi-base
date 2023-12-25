#! /usr/bin/env bash
set -e

python /app/celeryworker_pre_start.py

python /app/main.py
