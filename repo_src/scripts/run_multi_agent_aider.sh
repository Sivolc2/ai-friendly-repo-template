#!/usr/bin/env bash
# Script to run the multi-agent aider workflow in a virtual environment

set -e  # Exit on any error

# Ensure we're in the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create and activate virtual environment if it doesn't exist
VENV_DIR="./.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install/upgrade dependencies
echo "Installing required packages..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run the multi-agent aider workflow
echo "Starting multi-agent aider workflow..."
CONFIG_PATH="$SCRIPT_DIR/multi_agent_aider/config.yaml"
python -m multi_agent_aider.main_orchestrator --config "$CONFIG_PATH" "$@"

# Deactivate virtual environment
deactivate 