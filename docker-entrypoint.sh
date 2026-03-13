#!/bin/bash
set -e

# Wait for the database to be ready
echo "Waiting for database to be ready..."
# Simple check if DB_HOST and DB_PORT are reachable
until nc -z $DB_HOST $DB_PORT; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "Database is up!"

# Run database initialization
echo "Running database initialization (init_db.py)..."
python init_db.py

# If in development and rules are missing, we might want to seed full demo data
# This can be handled by seed_db.py if desired

# Execute the main application
echo "Starting the engine..."
exec python engine.py
