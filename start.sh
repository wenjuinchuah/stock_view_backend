#!/bin/bash

# Function to wait for MySQL to be fully ready
wait_for_mysql() {
  host="$1"
  shift
  until PING="$(mysqladmin ping -h"$host")"; do
    >&2 echo "MySQL is unavailable - sleeping"
    sleep 1
  done
  >&2 echo "MySQL is up - executing command"
}

# Wait for MySQL to be ready
wait_for_mysql db

# Run the application with --reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# Get the PID of the uvicorn process
UVICORN_PID=$!

# Wait for 10 seconds to let the first process start
sleep 10

# Send the SIGINT signal to the uvicorn process (simulating Ctrl + C)
kill -2 $UVICORN_PID

# Wait for the process to terminate
wait $UVICORN_PID

# Run the application with 3 workers
exec uvicorn app.main:app --workers 3 --host 0.0.0.0 --port 8000
