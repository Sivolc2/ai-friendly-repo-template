#!/bin/bash

# Reset script that kills processes using ports 8000 (backend) and 5173/5174 (frontend)
echo "Checking for processes using development ports..."

# Function to kill processes on a specific port
kill_port_process() {
  local PORT=$1
  local PIDS=$(lsof -ti :$PORT 2>/dev/null)
  
  if [ -n "$PIDS" ]; then
    echo "Found processes ($PIDS) using port $PORT, terminating..."
    kill $PIDS 2>/dev/null
    sleep 1
    # Check if processes are still running and force kill if necessary
    REMAINING=$(lsof -ti :$PORT 2>/dev/null)
    if [ -n "$REMAINING" ]; then
      echo "Force killing remaining processes on port $PORT..."
      kill -9 $REMAINING 2>/dev/null
    fi
    echo "Port $PORT is now free."
  else
    echo "No processes found using port $PORT."
  fi
}

# Kill processes on backend port
kill_port_process 8000

# Kill processes on frontend ports (Vite uses 5173 by default, may fall back to 5174)
kill_port_process 5173
kill_port_process 5174

echo "All development ports have been cleared."
echo "You can now run 'pnpm dev' to start the services." 