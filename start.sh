#!/bin/bash

# Run the application with --reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# Get the PID of the uvicorn process
UVICORN_PID=$!

# Wait for a few seconds to let the first process start
sleep 10

# Send the SIGINT signal to the uvicorn process (simulating Ctrl + C)
kill -SIGINT $UVICORN_PID

# Wait for the process to terminate
wait $UVICORN_PID

# Run the application with 3 workers
exec uvicorn app.main:app --workers 3 --host 0.0.0.0 --port 8000
