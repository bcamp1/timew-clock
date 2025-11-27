#!/bin/bash
# Setup script for clock - timewarrior wrapper

echo "Setting up clock..."
echo ""

# Create a symlink in ~/.local/bin or /usr/local/bin
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/clock.py"

# Try to create in ~/.local/bin first
if [ -d "$HOME/.local/bin" ]; then
    ln -sf "$SCRIPT_PATH" "$HOME/.local/bin/clock"
    echo "✓ Created symlink: $HOME/.local/bin/clock"
    echo ""
    if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
        echo "✓ $HOME/.local/bin is in your PATH"
    else
        echo "⚠ Add $HOME/.local/bin to your PATH to use 'clock' command"
        echo "  Add this to your ~/.bashrc or ~/.zshrc:"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
elif command -v sudo &> /dev/null; then
    sudo ln -sf "$SCRIPT_PATH" /usr/local/bin/clock
    echo "✓ Created symlink: /usr/local/bin/clock (requires sudo)"
else
    echo "✗ Could not create symlink automatically"
    echo ""
    echo "Please manually create a symlink:"
    echo "  ln -s $SCRIPT_PATH ~/.local/bin/clock"
    echo ""
    exit 1
fi

echo ""
echo "✓ Clock has been installed!"
echo ""
echo "Get started with:"
echo "  clock          # Show today's summary"
echo "  clock help     # Show all available commands"
echo ""
