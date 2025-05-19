#!/bin/bash

echo "Checking for processes using ports 5173 (Frontend) and 8000 (Backend)..."

# Check and kill process on port 5173 (Frontend)
PID_5173=$(lsof -t -i:5173)
if [ -n "$PID_5173" ]; then
    echo "Process using port 5173 found with PID: $PID_5173. Killing process..."
    kill -9 $PID_5173
    echo "Process on port 5173 killed."
else
    echo "No process found using port 5173."
fi

# Check and kill process on port 8000 (Backend)
PID_8000=$(lsof -t -i:8000)
if [ -n "$PID_8000" ]; then
    echo "Process using port 8000 found with PID: $PID_8000. Killing process..."
    kill -9 $PID_8000
    echo "Process on port 8000 killed."
else
    echo "No process found using port 8000."
fi

echo "Ports have been checked and reset if necessary." 