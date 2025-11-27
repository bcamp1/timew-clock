#!/bin/bash
# Setup script for clock - timewarrior wrapper

# Create a symlink in ~/.local/bin or /usr/local/bin
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/clock.py"

# Try to create in ~/.local/bin first
if [ -d "$HOME/.local/bin" ]; then
    ln -sf "$SCRIPT_PATH" "$HOME/.local/bin/clock"
    echo "Created symlink at $HOME/.local/bin/clock"
    echo "Make sure $HOME/.local/bin is in your PATH"
elif command -v sudo &> /dev/null; then
    sudo ln -sf "$SCRIPT_PATH" /usr/local/bin/clock
    echo "Created symlink at /usr/local/bin/clock"
else
    echo "Please manually create a symlink to $SCRIPT_PATH"
    echo "Example: ln -s $SCRIPT_PATH ~/.local/bin/clock"
fi
