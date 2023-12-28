#! /usr/bin/env bash
set -e

bash /prestart.sh

python /app/backend_pre_start.py

python /app/main.py
