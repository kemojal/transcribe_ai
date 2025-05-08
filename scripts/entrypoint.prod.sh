#!/bin/bash
set -e

# Wait for PostgreSQL to start
echo "Waiting for PostgreSQL to start..."
python -c "
import socket
import time
import os
import sys

host = 'db'
port = 5432
retry_count = 30
retry_interval = 5

for _ in range(retry_count):
    try:
        socket.create_connection((host, port), timeout=5)
        print('Database is ready!')
        break
    except (socket.timeout, socket.error) as e:
        retry_count -= 1
        if retry_count == 0:
            print(f'Could not connect to PostgreSQL after {retry_count} attempts')
            sys.exit(1)
        print(f'Waiting for database... {retry_count} retries left')
        print(f'Error: {e}')
        time.sleep(retry_interval)
"

# Run the database initialization script
echo "Running database initialization..."
python -m app.init_db

# Run database migrations
echo "Running database migrations..."
alembic -c alembic.ini upgrade head

# Start the application
echo "Starting the application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 