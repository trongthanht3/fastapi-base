#! /usr/bin/env bash

# Let the DB start
poetry run python /app/backend_pre_start.py

# Run migrations
echo "Running migrations"
poetry run alembic upgrade head
echo "Migrations finished"

# Create initial data in DB
poetry run python /app/initial_data.py
