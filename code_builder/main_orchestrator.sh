#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="${PROJECT_ROOT}/.venv"
REQUIREMENTS_PATH="${SCRIPT_DIR}/requirements.txt"
PYTHON_SCRIPT_PATH="${SCRIPT_DIR}/generate_plan.py"
LAUNCH_SCRIPT_PATH="${SCRIPT_DIR}/launch_aiders.sh"
NEEDS_INSTALL=false  # Initialize to false by default

# --- Check User Query ---
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 \"<Your feature request or query>\""
    exit 1
fi
USER_QUERY="$1"

# --- Find Suitable Python ---
# Function to check if a Python version is suitable
check_python_version() {
    local py_cmd="$1"
    if ! command -v "$py_cmd" &> /dev/null; then
        return 1
    fi
    echo "Found $py_cmd, checking version..."
    return 0
}

# Try to get the best Python version
if check_python_version "python3.11"; then
    PYTHON_CMD="python3.11"
    echo "Using Python 3.11"
elif check_python_version "python3.10"; then
    PYTHON_CMD="python3.10"  
    echo "Using Python 3.10"
elif check_python_version "python3.9"; then
    PYTHON_CMD="python3.9"
    echo "Using Python 3.9"
else
    PYTHON_CMD="python3"
    echo "Using default Python 3"
fi

# --- Setup Virtual Environment ---
if [ ! -d "$VENV_PATH" ]; then
    echo "Python virtual environment not found at $VENV_PATH. Creating..."
    
    # Create the virtual environment with the selected Python version
    echo "Creating virtual environment using $PYTHON_CMD..."
    $PYTHON_CMD -m venv "$VENV_PATH"
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        echo "Please ensure you have a compatible Python version installed."
        exit 1
    fi
    NEEDS_INSTALL=true
else
    echo "Found virtual environment at $VENV_PATH."
fi

# Activate venv
# shellcheck source=/dev/null
source "${VENV_PATH}/bin/activate"

# Check Python version in venv
PY_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Using Python version $PY_VERSION in virtual environment"

# Check/install requirements if venv was just created or if flag file is missing
INSTALL_FLAG="${VENV_PATH}/.pip_installed"
if [[ "$NEEDS_INSTALL" == "true" ]] || [ ! -f "$INSTALL_FLAG" ]; then
    echo "Installing/updating Python requirements from $REQUIREMENTS_PATH..."
    pip install --upgrade pip

    # Install Python requirements
    if ! pip install -r "$REQUIREMENTS_PATH"; then
        echo "Error: Failed to install Python requirements."
        echo "You might need a different Python version."
        exit 1
    fi
    
    touch "$INSTALL_FLAG" # Mark install as complete
    echo "Requirements installed."
    
    # Run aider-install
    echo "Setting up aider in its own environment..."
    python -m aider-install > /dev/null
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to run aider-install."
        exit 1
    fi
    echo "Aider installed successfully in its own environment."
fi

# Check if aider is available on the PATH
if ! command -v aider &> /dev/null; then
    echo "Error: 'aider' command not found in PATH."
    echo "This might be because aider-install didn't add it to your PATH."
    echo "You might need to restart your terminal or run 'aider-install' manually."
    echo "Trying to find aider in common installation locations..."
    
    # Try to find aider in common locations
    POTENTIAL_PATHS=(
        "$HOME/.local/bin/aider"
        "$HOME/Library/Python/*/bin/aider"
        "$HOME/.aider/bin/aider"
    )
    
    for path in "${POTENTIAL_PATHS[@]}"; do
        found_paths=$(ls $path 2>/dev/null || true)
        if [ -n "$found_paths" ]; then
            echo "Found aider at: $found_paths"
            echo "Please add this directory to your PATH and try again."
            break
        fi
    done
    
    # Try one more time with aider-install
    echo "Running aider-install one more time..."
    python -m aider-install
    
    # Force use of full path for aider in this session
    if [ -f "$HOME/.local/bin/aider" ]; then
        AIDER_CMD="$HOME/.local/bin/aider"
        echo "Using aider at $AIDER_CMD for this session."
    elif [ -d "$HOME/.aider/bin" ] && [ -f "$HOME/.aider/bin/aider" ]; then
        AIDER_CMD="$HOME/.aider/bin/aider"
        echo "Using aider at $AIDER_CMD for this session."
    else
        echo "Unable to locate aider. Please ensure it's installed and in your PATH."
        exit 1
    fi
else
    AIDER_CMD="aider"
    echo "Found aider in PATH."
fi

# --- Generate Run ID ---
RUN_ID=$(date +"%Y%m%d_%H%M%S")
echo "Starting Orchestration Run ID: $RUN_ID"

# --- Run Python Script to Generate PRD and Config ---
echo "Running Python script to generate PRD and Aider config..."
# Pass query and run ID to the python script
# Capture the output line containing the JSON path
output=$(python "$PYTHON_SCRIPT_PATH" "$USER_QUERY" --run-id "$RUN_ID")

# Extract the JSON path from the output
JSON_CONFIG_PATH=$(echo "$output" | grep '^JSON_CONFIG_PATH=' | cut -d'=' -f2)

if [[ -z "$JSON_CONFIG_PATH" || ! -f "$JSON_CONFIG_PATH" ]]; then
    echo "Error: Failed to get valid JSON config path from Python script."
    echo "Python script output:"
    echo "$output"
    exit 1
fi

echo "Python script finished. Aider config generated at: $JSON_CONFIG_PATH"

# --- Launch Aider Agents ---
echo "Launching Aider agents via tmux..."
# Export AIDER_CMD so launch_aiders.sh can use it
export AIDER_CMD
bash "$LAUNCH_SCRIPT_PATH" "$JSON_CONFIG_PATH" "$RUN_ID"

# --- Completion ---
echo "Orchestration script finished. Aider agents are running in tmux session: aider_session"
echo "Attach to session: tmux attach-session -t aider_session"
# Deactivate venv (optional, depends on workflow)
# deactivate 