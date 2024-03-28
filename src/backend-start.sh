#! /usr/bin/env bash
set -e

bash prestart.sh

poetry run python app/backend_pre_start.py

poetry run python app/main.py
