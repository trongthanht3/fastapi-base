#! /usr/bin/env bash
set -e

python /app/backend_pre_start.py

python /app/main.py
