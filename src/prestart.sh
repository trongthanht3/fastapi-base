#! /usr/bin/env bash

# Let the DB start
python /app/backend_pre_start.py

# Run migrations
echo "Running migrations"
alembic upgrade head
echo "Migrations finished"

# Create initial data in DB
python /app/initial_data.py
