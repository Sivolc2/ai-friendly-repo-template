#!/bin/bash

echo "Setting up environment files..."

# Define backend .env directory and file
BACKEND_ENV_DIR="repo_src/backend"
BACKEND_ENV_FILE="${BACKEND_ENV_DIR}/.env"

# Define frontend .env directory and file
FRONTEND_ENV_DIR="repo_src/frontend"
FRONTEND_ENV_FILE="${FRONTEND_ENV_DIR}/.env"

# Create backend .env file with default environment variables
if [ ! -f "$BACKEND_ENV_FILE" ]; then
    echo "Creating ${BACKEND_ENV_FILE} with default environment variables..."
    
    cat > "$BACKEND_ENV_FILE" << EOF
# Database configuration
DATABASE_URL=sqlite:///./app.db

# API settings
PORT=8000
LOG_LEVEL=info
EOF
    
    echo "${BACKEND_ENV_FILE} created."
else
    echo "${BACKEND_ENV_FILE} already exists. Skipping."
fi

# Create frontend .env file with default environment variables
if [ ! -f "$FRONTEND_ENV_FILE" ]; then
    echo "Creating ${FRONTEND_ENV_FILE} with default environment variables..."
    
    cat > "$FRONTEND_ENV_FILE" << EOF
# API URL (for direct API calls, not via proxy)
VITE_API_URL=http://localhost:8000
EOF
    
    echo "${FRONTEND_ENV_FILE} created."
else
    echo "${FRONTEND_ENV_FILE} already exists. Skipping."
fi

echo "Environment file setup complete."
echo "Please review the .env files in ${BACKEND_ENV_DIR} and ${FRONTEND_ENV_DIR} and customize if necessary." 