# Tmux Scripts for Aider

This directory contains scripts for managing Aider sessions using tmux on macOS.

## Available Scripts

### 1. `launch_aider_grid.sh`

Basic script that launches a 2x2 grid of Aider sessions.

```bash
./launch_aider_grid.sh
```

### 2. `aider-tmux.sh`

Flexible script with options for different layouts:

```bash
# Launch 4 Aider instances in a grid layout (default)
./aider-tmux.sh

# Launch 3 Aider instances horizontally
./aider-tmux.sh -l horizontal -n 3

# Launch 2 Aider instances vertically
./aider-tmux.sh -l vertical -n 2

# Use a specific Aider command
./aider-tmux.sh -c "aider --model gpt-4-turbo"

# Show help
./aider-tmux.sh --help
```

### 3. `ml-workspace.sh`

Specialized layout for machine learning workflows:

```bash
./ml-workspace.sh
```

## Prerequisites

- tmux: `brew install tmux`
- iTerm2: `brew install --cask iterm2` or download from [iterm2.com](https://iterm2.com)
- Aider: Install in a virtual environment with `pip install aider-chat`

## For More Information

See the full documentation at:
[../docs/context/README_tmux_iterm2.md](../docs/context/README_tmux_iterm2.md) 